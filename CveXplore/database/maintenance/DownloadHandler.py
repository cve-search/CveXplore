"""
Download Handler
================
"""
import datetime
import gzip
import json
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
from CveXplore.database.connection.mongo_db import MongoDBConnection
from .LogHandler import UpdateHandler
from .Toolkit import sanitize
from .worker_q import WorkerQueue

thread_local = threading.local()
logging.setLoggerClass(UpdateHandler)

logging.getLogger("urllib3").setLevel(logging.WARNING)


class DownloadHandler(ABC):
    """
    DownloadHandler is the base class for all downloads and subsequent processing of the downloaded content.
    Each download script has a derived class which handles specifics for that type of content / download.
    """

    def __init__(self, feed_type: str, prefix: str = None):
        self._end = None

        self.feed_type = feed_type

        self.prefix = prefix

        self.queue = WorkerQueue(name=self.feed_type)

        self.file_queue = WorkerQueue(name=f"{self.feed_type}:files")
        self.file_queue.clear()

        self.progress_bar = None

        self.last_modified = None

        self.do_process = True

        database = MongoDBConnection(**json.loads(os.getenv("MONGODB_CON_DETAILS")))

        self.database = database._dbclient

        self.logger = logging.getLogger("DownloadHandler")

        self.config = Configuration()

    def __repr__(self):
        """return string representation of object"""
        return "<< DownloadHandler:{} >>".format(self.feed_type)

    def get_session(
        self,
        retries: int = 1,
        backoff_factor: float = 0.3,
        status_forcelist: tuple = (429, 500, 502, 503, 504),
        session=None,
    ) -> requests.Session:
        """
        Method for returning a session object per every requesting thread
        """

        proxies = {"http": self.config.getProxy(), "https": self.config.getProxy()}

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

        thread_map(self.download_site, sites, desc="Downloading files")

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

        self.logger.info(
            "Duration: {}".format(timedelta(seconds=time.time() - start_time))
        )

    def chunk_list(self, lst: list, number: int) -> list:
        """
        Yield successive n-sized chunks from lst.
        """
        for i in range(0, len(lst), number):
            yield lst[i : i + number]

    def _db_bulk_writer(self, batch: list):
        """
        Method to act as worker for writing queued entries into the database
        """

        try:
            self.database[self.feed_type.lower()].bulk_write(batch, ordered=False)
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
            self.logger.debug("Saving file to: {}".format(filename))

            with zipfile.ZipFile(BytesIO(response_content)) as zip_file:
                zip_file.extractall(wd)

        elif (
            content_type == "application/x-gzip"
            or content_type == "application/gzip"
            or content_type == "application/x-gzip-compressed"
            or content_type == "application/gzip-compressed"
        ):
            filename = os.path.join(wd, url.split("/")[-1][:-3])
            self.logger.debug("Saving file to: {}".format(filename))

            buf = BytesIO(response_content)
            with open(filename, "wb") as f:
                f.write(gzip.GzipFile(fileobj=buf).read())

        elif (
            content_type == "application/json"
            or content_type == "application/xml"
            or content_type == "text/xml"
        ):
            filename = os.path.join(wd, url.split("/")[-1])
            self.logger.debug("Saving file to: {}".format(filename))

            with open(filename, "wb") as output_file:
                output_file.write(response_content)

        elif content_type == "application/local":
            filename = os.path.join(wd, url.split("/")[-1])
            self.logger.debug("Saving file to: {}".format(filename))

            copy(url[7:], filename)

        else:
            self.logger.error(
                "Unhandled Content-Type encountered: {} from url".format(
                    content_type, url
                )
            )
            sys.exit(1)

        return wd, filename

    def download_site(self, url: str):
        if url[:4] == "file":
            self.logger.info("Scheduling local hosted file: {}".format(url))

            # local file do not get last_modified header; so completely ignoring last_modified check and always asume
            # local file == the last modified file and set to current time.
            self.last_modified = datetime.datetime.now()

            self.logger.debug(
                "Last {} modified value: {} for URL: {}".format(
                    self.feed_type, self.last_modified, url
                )
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
            self.logger.debug("Downloading from url: {}".format(url))
            session = self.get_session()
            try:
                with session.get(url) as response:
                    try:
                        self.last_modified = parse_datetime(
                            response.headers["last-modified"], ignoretz=True
                        )
                    except KeyError:
                        self.logger.error(
                            "Did not receive last-modified header in the response; setting to default "
                            "(01-01-1970) and force update! Headers received: {}".format(
                                response.headers
                            )
                        )
                        # setting to last_modified to default value
                        self.last_modified = parse_datetime("01-01-1970")

                    self.logger.debug(
                        "Last {} modified value: {} for URL: {}".format(
                            self.feed_type, self.last_modified, url
                        )
                    )

                    i = self.getInfo(self.feed_type.lower())

                    if i is not None:
                        if self.last_modified == i["lastModified"]:
                            self.logger.info(
                                "{}'s are not modified since the last update".format(
                                    self.feed_type
                                )
                            )
                            self.file_queue.getall()
                            self.do_process = False
                    if self.do_process:
                        content_type = response.headers["content-type"]

                        self.logger.debug(
                            "URL: {} fetched Content-Type: {}".format(url, content_type)
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
                    "Exception encountered during download from: {}. Please check the logs for more information!".format(
                        url
                    )
                )
                self.logger.error(
                    "Exception encountered during the download from: {}. Error encountered: {}".format(
                        url, err
                    )
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
        return sanitize(self.database["cpe"].find_one(query))

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
