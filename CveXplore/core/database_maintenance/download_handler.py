"""
Download Handler
================
"""
import datetime
import gzip
import logging
import os
import sys
import tempfile
import threading
import time
import zipfile
from abc import ABC, abstractmethod
from datetime import timedelta
from io import BytesIO
from itertools import islice
from shutil import copy
from typing import Tuple

import requests
from dateutil.parser import parse as parse_datetime
from pymongo.errors import BulkWriteError, InvalidOperation
from requests.adapters import HTTPAdapter
from tqdm.contrib.concurrent import thread_map
from urllib3 import Retry

from CveXplore.common.config import Configuration
from CveXplore.core.general.utils import sanitize
from CveXplore.core.worker_queue.worker_q import WorkerQueue
from ..database_indexer.db_indexer import DatabaseIndexer
from ..logging.handlers.cve_explore_rfh import CveExploreUpdateRfhHandler
from ..logging.handlers.cve_explore_stream import CveExploreUpdateStreamHandler
from ..logging.logger_class import AppLogger
from ...database.connection.database_connection import DatabaseConnection

thread_local = threading.local()
logging.setLoggerClass(AppLogger)

logging.getLogger("urllib3").setLevel(logging.WARNING)


class DownloadHandler(ABC):
    """
    DownloadHandler is the base class for all downloads and subsequent processing of the downloaded content.
    Each download script has a derived class which handles specifics for that type of content / download.
    """

    def __init__(
        self,
        feed_type: str,
        logger_name: str,
        prefix: str = None,
    ):
        self.config = Configuration

        self._end = None

        self.feed_type = feed_type

        self.prefix = prefix

        self.queue = WorkerQueue(name=self.feed_type)

        self.file_queue = WorkerQueue(name=f"{self.feed_type}:files")
        self.file_queue.clear()

        self.progress_bar = None

        self.last_modified = None

        self.do_process = True

        database = DatabaseConnection(
            database_type=self.config.DATASOURCE_TYPE,
            database_init_parameters=self.config.DATASOURCE_CONNECTION_DETAILS,
        ).database_connection

        self.database = database.dbclient

        self.database_indexer = DatabaseIndexer(datasource=database)

        self.logger = logging.getLogger(logger_name)

        if len(self.logger.handlers) == 1:
            self.logger.removeHandler(self.logger.handlers[0])

        self.logger.propagate = False

        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        crf = None

        cli = CveExploreUpdateStreamHandler(stream=sys.stdout)
        cli.setFormatter(self.formatter)
        cli.setLevel(logging.INFO)

        if self.config.LOGGING_TO_FILE:
            crf = CveExploreUpdateRfhHandler(
                filename=f"{self.config.LOGGING_FILE_PATH}/{self.config.LOGGING_UPDATE_FILE_NAME}",
                maxBytes=self.config.LOGGING_MAX_FILE_SIZE,
                backupCount=self.config.LOGGING_BACKLOG,
            )
            crf.setLevel(logging.DEBUG)
            crf.setFormatter(self.formatter)

        if len(self.logger.handlers) > 0:
            for handler in self.logger.handlers:
                # add the handlers to the logger
                # makes sure no duplicate handlers are added
                if not isinstance(
                    handler, CveExploreUpdateRfhHandler
                ) and not isinstance(handler, CveExploreUpdateStreamHandler):
                    if crf is not None:
                        self.logger.addHandler(crf)
                    self.logger.addHandler(cli)
        else:
            if crf is not None:
                self.logger.addHandler(crf)
            self.logger.addHandler(cli)

    def __repr__(self):
        """return string representation of object"""
        return f"<< {self.__class__.__name__}:{self.feed_type} >>"

    def get_session(
        self,
        retries: int = 5,
        backoff_factor: float = 0.3,
        status_forcelist: tuple = (429, 500, 502, 503, 504),
        session=None,
    ) -> requests.Session:
        """
        Method for returning a session object per every requesting thread
        """

        proxies = self.config.HTTP_PROXY_DICT

        if not hasattr(thread_local, "session"):
            session = session or requests.Session()
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )

            session.proxies.update(proxies)

            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            thread_local.session = session

        return thread_local.session

    def process_downloads(self, sites: list):
        """
        Method to download and process files
        """

        start_time = time.time()

        self.logger.info(
            f"Downloading files (max {self.config.MAX_DOWNLOAD_WORKERS} workers)"
        )

        thread_map(
            self.download_site,
            sites,
            desc="Downloading files",
            max_workers=self.config.MAX_DOWNLOAD_WORKERS,
        )

        if self.do_process:
            thread_map(
                self.file_to_queue,
                self.file_queue.getall(),
                desc="Processing downloaded files",
            )

            chunks = []

            for batch in iter(lambda: list(islice(self.queue, 10000)), []):
                chunks.append(batch)

            thread_map(
                self._db_bulk_writer, chunks, desc="Transferring queue to database"
            )

            # checking if last-modified was in the response headers and not set to default
            if "01-01-1970" != self.last_modified.strftime("%d-%m-%Y"):
                self.setColUpdate(self.feed_type.lower(), self.last_modified)

        self.logger.info(f"Duration: {timedelta(seconds=time.time() - start_time)}")

    def chunk_list(self, lst: list, number: int) -> list:
        """
        Yield successive n-sized chunks from lst.
        """
        for i in range(0, len(lst), number):
            yield lst[i : i + number]

    def _db_bulk_writer(self, batch: list, initialization_run: bool = False):
        """
        Method to act as worker for writing queued entries into the database
        """

        try:
            if self.feed_type.lower() == "epss":
                self.database["cves"].bulk_write(batch, ordered=False)
            elif initialization_run and (
                self.feed_type.lower() == "cves" or self.feed_type.lower() == "cpe"
            ):
                # cves or cpe process item could yield None; so filter None from batch list
                self.database[self.feed_type.lower()].insert_many(
                    [x for x in batch if x is not None], ordered=False
                )
            else:
                self.database[self.feed_type.lower()].bulk_write(
                    [x for x in batch if x is not None], ordered=False
                )
        except BulkWriteError as err:
            self.logger.debug(f"Error during bulk write: {err}")
            pass
        except InvalidOperation as err:
            self.logger.debug(f"Got error during bulk update: {err}")
            pass
        except TypeError as err:
            self.logger.debug(f"Error during bulk write: {err}")
            raise

    def store_file(
        self, response_content: bytes, content_type: str, url: str
    ) -> Tuple[str, str]:
        """
        Method to store the download based on the headers content type
        """
        wd = tempfile.mkdtemp()
        filename = None

        if (
            content_type == "application/zip"
            or content_type == "application/x-zip"
            or content_type == "application/x-zip-compressed"
            or content_type == "application/zip-compressed"
        ):
            filename = os.path.join(wd, url.split("/")[-1][:-4])
            self.logger.debug(f"Saving file to: {filename}")

            with zipfile.ZipFile(BytesIO(response_content)) as zip_file:
                zip_file.extractall(wd)

        elif (
            content_type == "application/x-gzip"
            or content_type == "application/gzip"
            or content_type == "application/x-gzip-compressed"
            or content_type == "application/gzip-compressed"
        ):
            filename = os.path.join(wd, url.split("/")[-1][:-3])
            self.logger.debug(f"Saving file to: {filename}")

            buf = BytesIO(response_content)
            with open(filename, "wb") as f:
                f.write(gzip.GzipFile(fileobj=buf).read())

        elif (
            content_type == "application/json"
            or content_type == "application/xml"
            or content_type == "text/xml"
        ):
            filename = os.path.join(wd, url.split("/")[-1])
            self.logger.debug(f"Saving file to: {filename}")

            with open(filename, "wb") as output_file:
                output_file.write(response_content)

        elif content_type == "application/local":
            filename = os.path.join(wd, url.split("/")[-1])
            self.logger.debug(f"Saving file to: {filename}")

            copy(url[7:], filename)

        else:
            self.logger.error(
                f"Unhandled Content-Type encountered: {content_type} from url: {url}"
            )
            sys.exit(1)

        return wd, filename

    def download_site(self, url: str):
        if url[:4] == "file":
            self.logger.info(f"Scheduling local hosted file: {url}")

            # local file do not get last_modified header; so completely ignoring last_modified check and always asume
            # local file == the last modified file and set to current time.
            self.last_modified = datetime.datetime.now()

            self.logger.debug(
                f"Last {self.feed_type} modified value: {self.last_modified} for URL: {url}"
            )

            wd, filename = self.store_file(
                response_content=b"local", content_type="application/local", url=url
            )

            if filename is not None:
                self.file_queue.put((wd, filename))
            else:
                self.logger.error(
                    "Unable to retrieve a filename; something went wrong when trying to save the file"
                )
                sys.exit(1)

        else:
            self.logger.debug(f"Downloading from url: {url}")
            session = self.get_session()
            try:
                with session.get(url) as response:
                    try:
                        self.last_modified = parse_datetime(
                            response.headers["last-modified"], ignoretz=True
                        )
                    except KeyError:
                        self.logger.error(
                            f"Did not receive last-modified header in the response; setting to default "
                            f"(01-01-1970) and force update! Headers received: {response.headers}"
                        )
                        # setting to last_modified to default value
                        self.last_modified = parse_datetime("01-01-1970")

                    self.logger.debug(
                        f"Last {self.feed_type} modified value: {self.last_modified} for URL: {url}"
                    )

                    # epss releases on daily basis, if new cve's are inserted in the database
                    # it might be missing epss info, so always run the epss update
                    if self.feed_type.lower() != "epss":
                        i = self.getInfo(self.feed_type.lower())

                        if i is not None:
                            if self.last_modified == i["lastModified"]:
                                self.logger.info(
                                    f"{self.feed_type}'s are not modified since the last update"
                                )
                                self.file_queue.getall()
                                self.do_process = False

                    if self.do_process:
                        content_type = response.headers["content-type"]

                        self.logger.debug(
                            f"URL: {url} fetched Content-Type: {content_type}"
                        )

                        wd, filename = self.store_file(
                            response_content=response.content,
                            content_type=content_type,
                            url=url,
                        )

                        if filename is not None:
                            self.file_queue.put((wd, filename))
                        else:
                            self.logger.error(
                                "Unable to retrieve a filename; something went wrong when trying to save the file"
                            )
                            sys.exit(1)
            except Exception as err:
                self.logger.info(
                    f"Exception encountered during download from: {url}. Please check the logs for more information!"
                )
                self.logger.error(
                    f"Exception encountered during the download from: {url}. Error encountered: {err}"
                )
                self.do_process = False

    def dropCollection(self, col: str):
        return self.database[col].drop()

    def getTableNames(self):
        return self.database.list_collection_names()

    def setColInfo(self, collection: str, field: str, data: dict):
        self.database[collection].update_one(
            {"db": collection}, {"$set": {field: data}}, upsert=True
        )

    def delColInfo(self, collection: str):
        self.database["info"].delete_one({"db": collection})

    def getCPEVersionInformation(self, query: dict):
        return sanitize(self.database["cpe"].find(query))

    def getInfo(self, collection: str):
        return sanitize(self.database["info"].find_one({"db": collection}))

    def setColUpdate(self, collection: str, date: datetime):
        self.database["info"].update_one(
            {"db": collection}, {"$set": {"lastModified": date}}, upsert=True
        )

    @abstractmethod
    def process_item(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def file_to_queue(self, *args):
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def populate(self, **kwargs):
        raise NotImplementedError
