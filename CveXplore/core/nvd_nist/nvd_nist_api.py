import asyncio
import json
import logging
import math
import random
import time
import uuid
from collections import namedtuple
from datetime import datetime, timedelta
from json import JSONDecodeError
from urllib.parse import urlencode

import aiohttp as aiohttp
import requests
from aiohttp import ContentTypeError
from aioretry import retry, RetryPolicyStrategy, RetryInfo
from requests import Response
from requests.adapters import HTTPAdapter, Retry

from CveXplore.common.config import Configuration
from CveXplore.core.api_base_class import ApiBaseClass
from CveXplore.core.database_maintenance.update_base_class import UpdateBaseClass
from CveXplore.core.logging.logger_class import AppLogger
from CveXplore.errors.apis import (
    ApiErrorException,
    ApiDataError,
    ApiDataRetrievalFailed,
    ApiMaxRetryError,
)

logging.setLoggerClass(AppLogger)


class NvdNistApi(ApiBaseClass, UpdateBaseClass):
    def __init__(
        self,
        baseurl: str = "https://services.nvd.nist.gov",
        api_path: str = "2.0",
        proxies: dict = None,
        user_agent: str = "CveXplore",
    ):
        ApiBaseClass.__init__(
            self,
            baseurl=baseurl,
            api_path=api_path,
            user_agent=user_agent,
            proxies=proxies,
        )

        UpdateBaseClass.__init__(self, logger_name=__name__)

        if self.config.NVD_NIST_API_KEY is not None:
            self.api_key = self.config.NVD_NIST_API_KEY
            self.set_header_field("apiKey", self.api_key)
            self.api_key_limit = False
        else:
            self.logger.warning(
                "Could not find a NIST API Key in the environment variable 'NVD_NIST_API_KEY' "
                "(e.g. from the '~/.cvexplore/.env' file); "
                "you could request one at: https://nvd.nist.gov/developers/request-an-api-key"
            )
            self.api_key_limit = True

        self.filter_rejected = False

        if self.config.NVD_NIST_NO_REJECTED:
            self.filter_rejected = True

        self.datasource = namedtuple("datasource", "CVE CPE")(1, 2)

        self.datasource_mapping = {1: "cves", 2: "cpes"}

        self.max_page_length = namedtuple("max_page_length", "CVE CPE")(2000, 10000)

    def get_url_only(self, resource: dict = None, data: int = 1) -> str:
        return self._build_url(resource=resource, data=data)

    def _build_url(self, resource: dict = None, data: int = 1) -> str:
        if resource is not None:
            resource = urlencode(resource)
            if data == self.datasource.CVE:
                if self.filter_rejected:
                    return f"{self.baseurl}/rest/json/{self.datasource_mapping[data]}/{self.api_path}/?noRejected&{resource}"
                else:
                    return f"{self.baseurl}/rest/json/{self.datasource_mapping[data]}/{self.api_path}/?{resource}"
            else:
                return f"{self.baseurl}/rest/json/{self.datasource_mapping[data]}/{self.api_path}/?{resource}"
        else:
            if data == self.datasource.CVE:
                if self.filter_rejected:
                    return f"{self.baseurl}/rest/json/{self.datasource_mapping[data]}/{self.api_path}/?noRejected"
                else:
                    return f"{self.baseurl}/rest/json/{self.datasource_mapping[data]}/{self.api_path}/"
            else:
                return f"{self.baseurl}/rest/json/{self.datasource_mapping[data]}/{self.api_path}/"

    def _connect(
        self,
        method: str,
        resource: dict,
        session: requests.Session,
        data: dict = None,
        timeout: int = 60,
        return_response_object: bool = False,
    ):
        requests.packages.urllib3.disable_warnings()

        request_api_resource = {
            "headers": self.myheaders,
            "verify": self.verify,
            "timeout": timeout,
            "proxies": self.proxies,
        }

        try:
            self.logger.debug(f"Sending request: resource={resource}, data={data}")
            r = session.get(
                self._build_url(resource, data=data), **request_api_resource
            )

            try:
                if isinstance(r, Response):
                    if return_response_object:
                        return r
                    if r.status_code >= 400:
                        the_response = json.loads(r.text)
                        raise requests.exceptions.ConnectionError(the_response)
                    else:
                        the_response = json.loads(r.text)
                else:
                    the_response = r

            except JSONDecodeError:
                if "content-type" in r.headers:
                    if r.headers["content-type"] == "text/plain":
                        the_response = r.text
                    else:
                        the_response = r
                else:
                    the_response = r

            except Exception:
                the_response = r

            return the_response

        except requests.exceptions.ConnectionError as err:
            raise requests.exceptions.ConnectionError(err)
        except Exception as err:
            raise Exception(err)

    def __repr__(self):
        """return a string representation of the obj"""
        return f"<< NvdNistApi:{self.baseurl} >>"

    def get_cves_from_start_year(self):
        start_date = datetime(int(self.config.CVE_START_YEAR), 1, 1, 0, 0, 0, 0)
        start_date_iso = start_date.isoformat()

        end_date = start_date + timedelta(days=120)
        end_date_iso = end_date.isoformat()

        resource = {
            "pubStartDate": f"{start_date_iso}",
            "pubEndDate": f"{end_date_iso}",
        }

        return self.call("GET", resource=resource, data=self.datasource.CVE)

    def check_date_range(
        self,
        resource: dict = None,
        last_mod_start_date: datetime = None,
        last_mod_end_date: datetime = None,
    ):
        # Check if diff > 120 days
        diff = last_mod_end_date - last_mod_start_date

        if diff.days > 120:
            delta = diff.days - 120
            last_mod_end_date = last_mod_end_date - timedelta(delta)
            self.logger.warning(
                f"Requested timeframe exceeds the 120 days limit; capping the requested date range to 120 days. "
                f"End date is now: {last_mod_end_date.isoformat()}"
            )

        resource["lastModStartDate"] = last_mod_start_date.isoformat()
        resource["lastModEndDate"] = last_mod_end_date.isoformat()

        return resource

    def get_session(
        self,
        retries: int = 10,
        backoff_factor: float = 3,
        backoff_max: float = 30,
        status_forcelist: tuple = (403, 429, 500, 502, 503, 504),
        session=None,
    ) -> requests.Session:
        """
        Method for returning a session object per every requesting thread
        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            backoff_max=backoff_max,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get_count(
        self,
        datasource: int = 1,
        last_mod_start_date: datetime = None,
        last_mod_end_date: datetime = None,
    ):
        resource = {"resultsPerPage": 1}

        if last_mod_start_date is not None and last_mod_end_date is not None:
            resource = self.check_date_range(
                resource=resource,
                last_mod_start_date=last_mod_start_date,
                last_mod_end_date=last_mod_end_date,
            )

        self.logger.debug(f"Getting count for datasource: {datasource}")

        try:
            ret_data = self.call(self.methods.GET, resource=resource, data=datasource)

            if not isinstance(ret_data, Response):
                return ret_data["totalResults"]
            else:
                raise ApiDataRetrievalFailed(resource)
        except Exception:
            raise ApiMaxRetryError

    def get_all_data(
        self,
        data_type: str,
        last_mod_start_date: datetime = None,
        last_mod_end_date: datetime = None,
    ):
        resource = {}

        if last_mod_start_date is not None and last_mod_end_date is not None:
            self.logger.debug(f"Getting all updated {data_type}s....")
            resource = self.check_date_range(
                resource=resource,
                last_mod_start_date=last_mod_start_date,
                last_mod_end_date=last_mod_end_date,
            )
        else:
            self.logger.debug(f"Getting all {data_type}s...")

        try:
            data = self.get_count(
                getattr(self.datasource, data_type.upper()),
                last_mod_start_date=last_mod_start_date,
                last_mod_end_date=last_mod_end_date,
            )
        except ApiMaxRetryError:
            # failed to get the count; set data to 0 and continue
            data = 0

        if isinstance(data, int):
            for each_data in ApiData(
                results_per_page=getattr(self.max_page_length, data_type.upper()),
                start_index=0,
                total_results=data,
                api_handle=self,
                data_source=getattr(self.datasource, data_type.upper()),
                resource=resource,
            ):
                yield each_data
        else:
            raise ApiErrorException


class ApiData(object):
    def __init__(
        self,
        results_per_page: int,
        start_index: int,
        total_results: int,
        api_handle: NvdNistApi,
        data_source: int,
        resource=None,
    ):
        self.results_per_page = results_per_page
        self.start_index = start_index
        self.total_results = total_results
        self.api_handle = api_handle
        self.data_source = data_source
        self.resource = resource

    def __iter__(self):
        return ApiDataIterator(self)


def retry_policy(info: RetryInfo) -> RetryPolicyStrategy:
    """
    - It will always retry until succeeded
    - If fails for the first time, it will retry immediately,
    - If it fails again,

    aioretry will perform a 100ms delay before the second retry,
    200ms delay before the 3rd retry,
    the 4th retry immediately,
    100ms delay before the 5th retry,
    etc...
    """
    max_retries = 10
    backoff_in_s = 0.6 * 2**info.fails + random.uniform(0, 1) * 4
    logger = logging.getLogger(__name__)

    if info.fails != max_retries:
        logger.debug(
            f"Current backoff: {backoff_in_s}; Retrying {info.fails + 1}/{max_retries}"
        )
        return False, backoff_in_s
    else:
        return True, 0


class ApiDataIterator(object):
    def __init__(self, api_data: ApiData):
        self.logger = logging.getLogger(__name__)
        self.config = Configuration

        self._page_length = api_data.results_per_page
        self._total_results = api_data.total_results
        self._current_index = api_data.start_index
        self.api_data = api_data

        if self.config.DOWNLOAD_SEM_FACTOR != 0.0:
            self.sem_factor = self.config.DOWNLOAD_SEM_FACTOR
        else:
            self.sem_factor = 6

            if not self.api_data.api_handle.api_key_limit:
                self.sem_factor = 0.6

        self.logger.debug(f"Using sem factor: {self.sem_factor}")

        self.first_iteration = True

        self.last_stop_time = 0

        self.workload = None

    def __iter__(self):
        return self

    def __next__(self):
        if (
            self._current_index < self._total_results
            or self._page_length == self._total_results
        ):
            start_time = time.time()

            if not self.last_stop_time == 0:
                # adhering to best practices @https://nvd.nist.gov/general/news/API-Key-Announcement
                # which advises to sleep for 6 seconds, so we add this to the 30 seconds rolling window; hence 36
                sleep_time = start_time - self.last_stop_time
                if sleep_time <= 36:
                    self.logger.debug(
                        f"36 second window not expired; sleeping for : {36 - sleep_time}"
                    )
                    time.sleep(36 - sleep_time)

            self.logger.debug(f"Starting download run...")

            self.workload = []

            if self.config.DOWNLOAD_BATCH_RANGE is None:
                if self.api_data.api_handle.api_key_limit:
                    batch_range = 5
                else:
                    batch_range = 45
            else:
                try:
                    batch_range = int(self.config.DOWNLOAD_BATCH_RANGE)
                except ValueError:
                    self.logger.error(
                        f"Invalid value for DOWNLOAD_BATCH_RANGE, {self.config.DOWNLOAD_BATCH_RANGE} "
                        f"cannot be converted into an integer..."
                    )
                    raise

            for i in range(batch_range):
                if not self.first_iteration:
                    new_start_index = self._current_index + self._page_length
                else:
                    new_start_index = self._current_index
                    self.first_iteration = False

                self._current_index = new_start_index
                resource = {"startIndex": new_start_index}
                if self.api_data.resource is not None:
                    resource = {**resource, **self.api_data.resource}
                if new_start_index > self._total_results:
                    break
                self.workload.append(
                    self.api_data.api_handle.get_url_only(
                        resource=resource, data=self.api_data.data_source
                    )
                )

            ret_data = self.process_async()

            self.last_stop_time = time.time()
            elapsed_time = self.last_stop_time - start_time

            self.logger.debug(f"Elapsed run time: {elapsed_time}")

            return ret_data

        raise StopIteration

    def process_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self.fetch_all(loop))

        return results

    @retry(retry_policy)
    async def fetch(self, session: aiohttp.ClientSession, url: str):
        request_id = uuid.uuid4()
        try:
            async with session.get(
                url, proxy=self.config.HTTP_PROXY_STRING
            ) as response:
                self.logger.debug(f"[{request_id}] Sending request to url: {url}")
                if response.status == 200:
                    data = await response.json()
                    if "format" in data:
                        if data["format"] == "NVD_CPE":
                            if "products" not in data:
                                self.logger.debug(
                                    f"Data received does not contain a products list; raise error to retry!"
                                )
                                raise ApiDataError
                        elif data["format"] == "NVD_CVE":
                            if "vulnerabilities" not in data:
                                self.logger.debug(
                                    f"Data received does not contain a vulnerabilities list; raise error to retry!"
                                )
                                raise ApiDataError
                        else:
                            self.logger.debug(
                                f"Data received does not match expected formatting string; raise error to retry!"
                            )
                            raise ApiDataError
                    else:
                        self.logger.debug(
                            f"Data received does not match expected content; raise error to retry!"
                        )
                        raise ApiDataError
                    return data
                else:
                    if str(response.status).startswith("4"):
                        if "message" in response.headers:
                            self.logger.debug(response.headers["message"])
                    if response.status == 403:
                        self.logger.debug(f"Request forbidden by administrative rules")
                    raise ApiDataRetrievalFailed(url)
        except ApiDataError:
            raise
        except ContentTypeError:
            return ApiDataRetrievalFailed(url)
        finally:
            random_sleep = round(
                random.SystemRandom().uniform(
                    self.config.DOWNLOAD_SLEEP_MIN, self.config.DOWNLOAD_SLEEP_MAX
                ),
                1,
            )
            self.logger.debug(f"[{request_id}] Sleeping for {random_sleep} secs...")
            await asyncio.sleep(random_sleep)
            self.logger.debug(f"[{request_id}] Finished request")

    async def fetch_all(self, loop):
        sem = asyncio.Semaphore(math.ceil(30 / self.sem_factor))
        async with sem:
            async with aiohttp.ClientSession(
                loop=loop,
                headers=self.api_data.api_handle.headers,
                timeout=aiohttp.ClientTimeout(
                    total=30.0, sock_connect=30.0, sock_read=30.0, connect=30.0
                ),
            ) as session:
                results = await asyncio.gather(
                    *[
                        self.fetch(
                            session,
                            entry,
                        )
                        for entry in self.workload
                    ],
                    return_exceptions=True,
                )
                return results
