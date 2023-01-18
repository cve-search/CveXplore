import asyncio
import json
import logging
import math
from collections import namedtuple
from datetime import datetime, timedelta
from json import JSONDecodeError
from urllib.parse import urlencode

import aiohttp as aiohttp
import requests

from CveXplore.common.config import Configuration
from CveXplore.common.generic_api import GenericApi
from CveXplore.database.maintenance.LogHandler import UpdateHandler
from CveXplore.errors.apis import ApiErrorException

logging.setLoggerClass(UpdateHandler)


class NvdNistApi(GenericApi):
    def __init__(
        self,
        address=("services.nvd.nist.gov", 443),
        api_path="2.0",
        user_agent="CveXplore",
    ):
        super().__init__(address, api_path=api_path, user_agent=user_agent)

        self.config = Configuration()

        self.logger = logging.getLogger("NvdNistApi")

        if self.config.NVD_NIST_API_KEY is not None:
            self.api_key = self.config.NVD_NIST_API_KEY
            self.set_header_field("apiKey", self.api_key)
            self.api_key_limit = False
        else:
            self.api_key_limit = True

        self.filter_rejected = False

        if self.config.NVD_NIST_NO_REJECTED:
            self.filter_rejected = True

        self.datasource = namedtuple("datasource", "CVE CPE")(1, 2)

        self.datasource_mapping = {1: "cves", 2: "cpes"}

        self.NVD_SOURCES = {
            "cve": "https://services.nvd.nist.gov/rest/json/cves/2.0",
            "cpe": "https://services.nvd.nist.gov/rest/json/cpes/2.0",
        }

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
        self, method, resource: dict, session: requests.Session, data=None, timeout=60
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
                json_response = json.loads(r.text)
            except JSONDecodeError:
                json_response = r

            return json_response
        except requests.exceptions.ConnectionError:
            raise ConnectionError

    def __repr__(self):
        """return a string representation of the obj GenericApi"""
        return f"<<NvdNistApi:({self.server}, {self.port})>>"

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

    def get_all_cves(self):

        data = self.get_count(self.datasource.CVE)

        if isinstance(data, int):

            for each_data in ApiData(
                2000,
                0,
                data,
                self,
                self.datasource.CVE,
            ):
                yield each_data
        else:
            raise ApiErrorException

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

        if datasource == self.datasource.CVE:
            ret_data = self.call("GET", resource=resource, data=self.datasource.CVE)
        else:
            ret_data = self.call("GET", resource=resource, data=self.datasource.CPE)

        return ret_data["totalResults"]

    def get_all_cpes(
        self,
        last_mod_start_date: datetime = None,
        last_mod_end_date: datetime = None,
    ):

        resource = {}

        if last_mod_start_date is not None and last_mod_end_date is not None:
            self.logger.debug("Getting all updated cpes....")
            resource = self.check_date_range(
                resource=resource,
                last_mod_start_date=last_mod_start_date,
                last_mod_end_date=last_mod_end_date,
            )
        else:
            self.logger.debug("Getting all cpes...")

        data = self.get_count(
            self.datasource.CPE,
            last_mod_start_date=last_mod_start_date,
            last_mod_end_date=last_mod_end_date,
        )

        if isinstance(data, int):

            for each_data in ApiData(
                results_per_page=10000,
                start_index=0,
                total_results=data,
                api_handle=self,
                data_source=self.datasource.CPE,
                resource=resource,
            ):
                yield each_data
        else:
            raise ApiErrorException


class ApiData(object):
    def __init__(
        self,
        results_per_page,
        start_index,
        total_results,
        api_handle: NvdNistApi,
        data_source,
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


class ApiDataIterator(object):
    def __init__(self, api_data: ApiData):
        self.logger = logging.getLogger("ApiDataIterator")

        self._page_length = api_data.results_per_page
        self._total_results = api_data.total_results
        self._current_index = api_data.start_index
        self.api_data = api_data

        self.sleep_time = 6

        if not self.api_data.api_handle.api_key_limit:
            self.sleep_time = 0.75

        self.logger.debug(f"Using sleep time: {self.sleep_time}")

        self.first_iteration = True

        self.workload = None

    def __iter__(self):
        return self

    def __next__(self):

        if (
            self._current_index < self._total_results
            or self._page_length == self._total_results
        ):

            self.workload = []

            if self.api_data.api_handle.api_key_limit:
                api_key_range = 25
            else:
                api_key_range = 40

            for i in range(api_key_range):
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

            return ret_data

        raise StopIteration

    def process_async(self):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self.fetch_all(loop))

        return results

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                self.logger.debug(f"Sending request to url: {url}")
                # time.sleep(self.sleep_time)
                data = await response.json()
                return data
        except Exception as err:
            return {"ERROR": f"Error getting {url} data.... Error observed: {err}"}

    async def fetch_all(self, loop):
        sem = asyncio.Semaphore(math.ceil(30 / self.sleep_time))
        async with sem:
            async with aiohttp.ClientSession(
                loop=loop,
                headers=self.api_data.api_handle.headers,
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
