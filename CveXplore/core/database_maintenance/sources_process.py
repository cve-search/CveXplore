"""
Source processing classes
=========================
"""
import datetime
import glob
import hashlib
import json
import shutil
import time
from typing import Any, Tuple
from xml.sax import make_parser

from dateutil.parser import parse as parse_datetime
from tqdm import tqdm

from CveXplore.core.database_actions.db_action import DatabaseAction
from CveXplore.core.database_maintenance.api_handlers import NVDApiHandler
from CveXplore.core.database_maintenance.content_handlers import (
    CapecHandler,
    CWEHandler,
)
from CveXplore.core.database_maintenance.file_handlers import (
    XMLFileHandler,
    JSONFileHandler,
    CSVFileHandler,
)
from CveXplore.errors.apis import ApiDataRetrievalFailed, ApiMaxRetryError

date = datetime.datetime.now()
year = date.year + 1

# default config
defaultvalue = {"cwe": "Unknown"}


class CPEDownloads(NVDApiHandler):
    """
    Class processing CPE source files
    """

    def __init__(self):
        self.feed_type = "CPE"

        super().__init__(feed_type=self.feed_type, logger_name=__name__)

    def file_to_queue(self, *args):
        pass

    @staticmethod
    def parse_cpe_version(cpename: str):
        cpe_list = cpename.split(":")
        version_stem = cpe_list[5]

        if cpe_list[6] != "*" and cpe_list[6] != "-":
            return f"{version_stem}.{cpe_list[6]}"
        else:
            return version_stem

    def process_the_item(self, item: dict = None):
        if item is None:
            return None

        item = item["cpe"]

        # filter out deprecated CPE's if CPE_FILTER_DEPRECATED is set to True
        if self.config.CPE_FILTER_DEPRECATED:
            if item["deprecated"]:
                return None

        if "cpeName" not in item:
            return None

        title = None

        if "titles" in item:
            for t in item["titles"]:
                if t["lang"] == "en":
                    title = t["title"]

        version = self.parse_cpe_version(cpename=item["cpeName"])

        cpe = {
            "title": title,
            "cpeName": item["cpeName"],
            "vendor": item["cpeName"].split(":")[3],
            "product": item["cpeName"].split(":")[4],
            "version": version,
            "padded_version": self.padded_version(version),
            "stem": self.stem(item["cpeName"]),
            "cpeNameId": item["cpeNameId"],
            "lastModified": parse_datetime(item["lastModified"], ignoretz=True),
            "created": parse_datetime(item["created"], ignoretz=True),
            "deprecated": item["deprecated"],
            "deprecatedBy": item["deprecatedBy"] if item["deprecated"] else "",
        }

        sha1_hash = hashlib.sha1(
            cpe["cpeName"].encode("utf-8")
            + item["cpeName"].split(":")[5].encode("utf-8")
        ).hexdigest()

        cpe["id"] = sha1_hash

        return cpe

    def process_downloads(self, sites: list = None):
        """
        Method to download and process files
        """

        self.logger.info("Starting download...")

        start_time = time.time()

        self.last_modified = datetime.datetime.now()

        self.logger.debug(
            f"do_process = {self.do_process}; is_update = {self.is_update}"
        )

        if self.do_process:
            if not self.is_update:
                try:
                    total_results = self.api_handler.get_count(
                        self.api_handler.datasource.CPE
                    )
                except ApiMaxRetryError:
                    # failed to get the count; set total_results to 0 and continue
                    total_results = 0

                self.logger.info(f"Preparing to download {total_results} CPE entries")

                with tqdm(
                    desc="Downloading and processing content",
                    total=total_results,
                    position=0,
                    leave=True,
                ) as pbar:
                    for entry in self.api_handler.get_all_data(data_type="cpe"):
                        # do something here with the results...
                        for data_list in tqdm(
                            entry, desc=f"Processing batch", leave=False
                        ):
                            if not isinstance(data_list, ApiDataRetrievalFailed):
                                if not isinstance(data_list, Exception):
                                    processed_items = [
                                        self.process_item(item)
                                        for item in data_list["products"]
                                    ]
                                    self._db_bulk_writer(
                                        processed_items, initialization_run=True
                                    )
                                    pbar.update(len(data_list["products"]))
                                else:
                                    self.logger.error(
                                        f"Retrieval of api data resulted in an Exception: {data_list}..."
                                    )
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )
            else:
                last_mod_start_date = self.database[self.feed_type.lower()].find_one(
                    {}, {"lastModified": 1}, sort=[("lastModified", -1)]
                )

                if last_mod_start_date is not None:
                    if "lastModified" in last_mod_start_date:
                        last_mod_start_date = last_mod_start_date[
                            "lastModified"
                        ] + datetime.timedelta(
                            0, 1
                        )  # add one second to prevent false results...
                    else:
                        raise KeyError(
                            "Missing field 'lastModified' from database query..."
                        )
                else:
                    self.logger.warning(
                        "No records found in the mongodb cpe collection.."
                    )
                    return

                    # Get datetime from runtime
                last_mod_end_date = datetime.datetime.now()

                try:
                    total_results = self.api_handler.get_count(
                        self.api_handler.datasource.CPE,
                        last_mod_start_date=last_mod_start_date,
                        last_mod_end_date=last_mod_end_date,
                    )
                except ApiMaxRetryError:
                    # failed to get the count; set total_results to 0 and continue
                    total_results = 0

                self.logger.info(f"Preparing to download {total_results} CPE entries")

                with tqdm(
                    desc="Downloading and processing content",
                    total=total_results,
                    position=0,
                    leave=True,
                ) as pbar:
                    for entry in self.api_handler.get_all_data(
                        data_type="cpe",
                        last_mod_start_date=last_mod_start_date,
                        last_mod_end_date=last_mod_end_date,
                    ):
                        # do something here with the results...
                        for data_list in tqdm(
                            entry, desc=f"Processing batch", leave=False
                        ):
                            if not isinstance(data_list, ApiDataRetrievalFailed):
                                if not isinstance(data_list, Exception):
                                    processed_items = [
                                        self.process_item(item)
                                        for item in data_list["products"]
                                    ]
                                    self._db_bulk_writer(processed_items)
                                    pbar.update(len(data_list["products"]))
                                else:
                                    self.logger.error(
                                        f"Retrieval of api data resulted in an Exception: {data_list}..."
                                    )
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )

            # Set the last update time in the info collection
            self.setColUpdate(self.feed_type.lower(), self.last_modified)

        self.logger.info(
            f"Duration: {datetime.timedelta(seconds=time.time() - start_time)}"
        )

    def update(self, **kwargs):
        self.logger.info("CPE database update started")

        self.process_downloads()

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            self.database_indexer.create_indexes(collection=self.feed_type.lower())
            self.is_update = False

        self.logger.info("Finished CPE database update")

        return self.last_modified

    def populate(self, **kwargs):
        self.logger.info("CPE Database population started")

        self.is_update = False

        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        self.process_downloads()

        self.database_indexer.create_indexes(collection=self.feed_type.lower())

        self.logger.info("Finished CPE database population")

        return self.last_modified


class CVEDownloads(NVDApiHandler):
    """
    Class processing CVE source files
    """

    def __init__(self):
        self.feed_type = "CVES"

        super().__init__(feed_type=self.feed_type, logger_name=__name__)

    def get_cpe_info(self, cpeuri: str):
        query = {}

        if "versionStartExcluding" in cpeuri:
            if "versionEndExcluding" in cpeuri:
                query = {
                    "deprecated": False,
                    "stem": self.stem(cpeuri["criteria"]),
                    "padded_version": {
                        "$gt": self.padded_version(cpeuri["versionStartExcluding"]),
                        "$lt": self.padded_version(cpeuri["versionEndExcluding"]),
                    },
                }
            elif "versionEndIncluding" in cpeuri:
                query = {
                    "deprecated": False,
                    "stem": self.stem(cpeuri["criteria"]),
                    "padded_version": {
                        "$gt": self.padded_version(cpeuri["versionStartExcluding"]),
                        "$lte": self.padded_version(cpeuri["versionEndIncluding"]),
                    },
                }
            else:
                query = {
                    "deprecated": False,
                    "stem": self.stem(cpeuri["criteria"]),
                    "padded_version": {
                        "$gt": self.padded_version(cpeuri["versionStartExcluding"])
                    },
                }

        elif "versionStartIncluding" in cpeuri:
            if "versionEndExcluding" in cpeuri:
                query = {
                    "deprecated": False,
                    "stem": self.stem(cpeuri["criteria"]),
                    "padded_version": {
                        "$gte": self.padded_version(cpeuri["versionStartIncluding"]),
                        "$lt": self.padded_version(cpeuri["versionEndExcluding"]),
                    },
                }
            elif "versionEndIncluding" in cpeuri:
                query = {
                    "deprecated": False,
                    "stem": self.stem(cpeuri["criteria"]),
                    "padded_version": {
                        "$gte": self.padded_version(cpeuri["versionStartIncluding"]),
                        "$lte": self.padded_version(cpeuri["versionEndIncluding"]),
                    },
                }
            else:
                query = {
                    "deprecated": False,
                    "stem": self.stem(cpeuri["criteria"]),
                    "padded_version": {
                        "$gte": self.padded_version(cpeuri["versionStartIncluding"])
                    },
                }

        elif "versionEndExcluding" in cpeuri:
            query = {
                "deprecated": False,
                "stem": self.stem(cpeuri["criteria"]),
                "padded_version": {
                    "$lt": self.padded_version(cpeuri["versionEndExcluding"])
                },
            }

        elif "versionEndIncluding" in cpeuri:
            query = {
                "deprecated": False,
                "stem": self.stem(cpeuri["criteria"]),
                "padded_version": {
                    "$lte": self.padded_version(cpeuri["versionEndIncluding"])
                },
            }

        return query

    @staticmethod
    def add_if_missing(cve: dict, key: str, value: Any):
        if value not in cve[key]:
            cve[key].append(value)
        return cve

    @staticmethod
    def get_vendor_product(cpeUri: str):
        vendor = cpeUri.split(":")[3]
        product = cpeUri.split(":")[4]
        return vendor, product

    def file_to_queue(self, *args):
        pass

    def process_the_item(self, item: dict = None):
        if item is None:
            return None

        cve = {
            "id": item["cve"]["id"],
            "assigner": item["cve"]["sourceIdentifier"],
            "status": item["cve"]["vulnStatus"],
            "published": parse_datetime(item["cve"]["published"], ignoretz=True),
            "modified": parse_datetime(item["cve"]["lastModified"], ignoretz=True),
            "lastModified": parse_datetime(item["cve"]["lastModified"], ignoretz=True),
        }

        for description in item["cve"]["descriptions"]:
            if description["lang"] == "en":
                if "summary" in cve:
                    cve["summary"] += f" {description['value']}"
                else:
                    cve["summary"] = description["value"]

        if "metrics" in item["cve"]:
            cve["access"] = {}
            cve["impact"] = {}
            if "cvssMetricV31" in item["cve"]["metrics"]:
                cve["impact3"] = {}
                cve["exploitability3"] = {}
                cve["impact3"]["availability"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["availabilityImpact"]
                cve["impact3"]["confidentiality"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["confidentialityImpact"]
                cve["impact3"]["integrity"] = item["cve"]["metrics"]["cvssMetricV31"][
                    0
                ]["cvssData"]["integrityImpact"]
                cve["exploitability3"]["attackvector"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["attackVector"]
                cve["exploitability3"]["attackcomplexity"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["attackComplexity"]
                cve["exploitability3"]["privilegesrequired"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["privilegesRequired"]
                cve["exploitability3"]["userinteraction"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["userInteraction"]
                cve["exploitability3"]["scope"] = item["cve"]["metrics"][
                    "cvssMetricV31"
                ][0]["cvssData"]["scope"]
                cve["cvss3"] = float(
                    item["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"]
                )
                cve["cvss3Vector"] = item["cve"]["metrics"]["cvssMetricV31"][0][
                    "cvssData"
                ]["vectorString"]
                cve["impactScore3"] = float(
                    item["cve"]["metrics"]["cvssMetricV31"][0]["impactScore"]
                )
                cve["exploitabilityScore3"] = float(
                    item["cve"]["metrics"]["cvssMetricV31"][0]["exploitabilityScore"]
                )
                cve["cvss3Time"] = parse_datetime(
                    item["cve"]["lastModified"], ignoretz=True
                )
                cve["cvss3Type"] = item["cve"]["metrics"]["cvssMetricV31"][0]["type"]
                cve["cvss3Source"] = item["cve"]["metrics"]["cvssMetricV31"][0][
                    "source"
                ]
            elif "cvssMetricV30" in item["cve"]["metrics"]:
                cve["impact3"] = {}
                cve["exploitability3"] = {}
                cve["impact3"]["availability"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["availabilityImpact"]
                cve["impact3"]["confidentiality"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["confidentialityImpact"]
                cve["impact3"]["integrity"] = item["cve"]["metrics"]["cvssMetricV30"][
                    0
                ]["cvssData"]["integrityImpact"]
                cve["exploitability3"]["attackvector"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["attackVector"]
                cve["exploitability3"]["attackcomplexity"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["attackComplexity"]
                cve["exploitability3"]["privilegesrequired"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["privilegesRequired"]
                cve["exploitability3"]["userinteraction"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["userInteraction"]
                cve["exploitability3"]["scope"] = item["cve"]["metrics"][
                    "cvssMetricV30"
                ][0]["cvssData"]["scope"]
                cve["cvss3"] = float(
                    item["cve"]["metrics"]["cvssMetricV30"][0]["cvssData"]["baseScore"]
                )
                cve["cvss3Vector"] = item["cve"]["metrics"]["cvssMetricV30"][0][
                    "cvssData"
                ]["vectorString"]
                cve["impactScore3"] = float(
                    item["cve"]["metrics"]["cvssMetricV30"][0]["impactScore"]
                )
                cve["exploitabilityScore3"] = float(
                    item["cve"]["metrics"]["cvssMetricV30"][0]["exploitabilityScore"]
                )
                cve["cvss3Time"] = parse_datetime(
                    item["cve"]["lastModified"], ignoretz=True
                )
                cve["cvss3Type"] = item["cve"]["metrics"]["cvssMetricV30"][0]["type"]
                cve["cvss3Source"] = item["cve"]["metrics"]["cvssMetricV30"][0][
                    "source"
                ]
            else:
                cve["cvss3"] = None

            if "cvssMetricV2" in item["cve"]["metrics"]:
                cve["access"]["authentication"] = item["cve"]["metrics"][
                    "cvssMetricV2"
                ][0]["cvssData"]["authentication"]
                cve["access"]["complexity"] = item["cve"]["metrics"]["cvssMetricV2"][0][
                    "cvssData"
                ]["accessComplexity"]
                cve["access"]["vector"] = item["cve"]["metrics"]["cvssMetricV2"][0][
                    "cvssData"
                ]["accessVector"]
                cve["impact"]["availability"] = item["cve"]["metrics"]["cvssMetricV2"][
                    0
                ]["cvssData"]["availabilityImpact"]
                cve["impact"]["confidentiality"] = item["cve"]["metrics"][
                    "cvssMetricV2"
                ][0]["cvssData"]["confidentialityImpact"]
                cve["impact"]["integrity"] = item["cve"]["metrics"]["cvssMetricV2"][0][
                    "cvssData"
                ]["integrityImpact"]
                cve["cvss"] = float(
                    item["cve"]["metrics"]["cvssMetricV2"][0]["cvssData"]["baseScore"]
                )
                cve["exploitabilityScore"] = float(
                    item["cve"]["metrics"]["cvssMetricV2"][0]["exploitabilityScore"]
                )
                cve["impactScore"] = float(
                    item["cve"]["metrics"]["cvssMetricV2"][0]["impactScore"]
                )
                cve["cvssTime"] = parse_datetime(
                    item["cve"]["lastModified"], ignoretz=True
                )  # NVD JSON lacks the CVSS time which was present in the original XML format
                cve["cvssVector"] = item["cve"]["metrics"]["cvssMetricV2"][0][
                    "cvssData"
                ]["vectorString"]
                cve["cvssType"] = item["cve"]["metrics"]["cvssMetricV2"][0]["type"]
                cve["cvssSource"] = item["cve"]["metrics"]["cvssMetricV2"][0]["source"]
            else:
                cve["cvss"] = None

        if "references" in item["cve"]:
            cve["references"] = []
            for ref in item["cve"]["references"]:
                cve["references"].append(ref["url"])

        if "configurations" in item["cve"]:
            cve["vulnerable_configuration"] = []
            cve["vulnerable_product"] = []
            cve["vendors"] = []
            cve["products"] = []
            cve["vulnerable_product_stems"] = []
            cve["vulnerable_configuration_stems"] = []
            for node in item["cve"]["configurations"]:
                for cpe in node["nodes"]:
                    if "cpeMatch" in cpe:
                        for cpeuri in cpe["cpeMatch"]:
                            if "criteria" not in cpeuri:
                                continue
                            if cpeuri["vulnerable"]:
                                query = self.get_cpe_info(cpeuri)
                                if query != {}:
                                    cpe_info = sorted(
                                        self.getCPEVersionInformation(query),
                                        key=lambda x: x["padded_version"],
                                    )
                                    if cpe_info:
                                        if not isinstance(cpe_info, list):
                                            cpe_info = [cpe_info]

                                        for vulnerable_version in cpe_info:
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_product",
                                                vulnerable_version["cpeName"],
                                            )
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_configuration",
                                                vulnerable_version["cpeName"],
                                            )
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_configuration_stems",
                                                vulnerable_version["stem"],
                                            )

                                            cve = self.add_if_missing(
                                                cve,
                                                "vendors",
                                                vulnerable_version["vendor"],
                                            )

                                            cve = self.add_if_missing(
                                                cve,
                                                "products",
                                                vulnerable_version["product"],
                                            )

                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_product_stems",
                                                vulnerable_version["stem"],
                                            )
                                else:
                                    # If the cpeMatch did not have any of the version start/end modifiers,
                                    # add the CPE string as it is.
                                    cve = self.add_if_missing(
                                        cve, "vulnerable_product", cpeuri["criteria"]
                                    )
                                    cve = self.add_if_missing(
                                        cve,
                                        "vulnerable_configuration",
                                        cpeuri["criteria"],
                                    )
                                    cve = self.add_if_missing(
                                        cve,
                                        "vulnerable_configuration_stems",
                                        self.stem(cpeuri["criteria"]),
                                    )
                                    vendor, product = self.get_vendor_product(
                                        cpeuri["criteria"]
                                    )
                                    cve = self.add_if_missing(cve, "vendors", vendor)
                                    cve = self.add_if_missing(cve, "products", product)
                                    cve = self.add_if_missing(
                                        cve,
                                        "vulnerable_product_stems",
                                        self.stem(cpeuri["criteria"]),
                                    )
                            else:
                                cve = self.add_if_missing(
                                    cve, "vulnerable_configuration", cpeuri["criteria"]
                                )
                                cve = self.add_if_missing(
                                    cve,
                                    "vulnerable_configuration_stems",
                                    self.stem(cpeuri["criteria"]),
                                )
        if "weaknesses" in item["cve"]:
            for problem in item["cve"]["weaknesses"]:
                for cwe in problem[
                    "description"
                ]:  # NVD JSON not clear if we can get more than one CWE per CVE (until we take the last one) -
                    # NVD-CWE-Other??? list?
                    if cwe["lang"] == "en":
                        cve["cwe"] = cwe["value"]
            if not ("cwe" in cve):
                cve["cwe"] = defaultvalue["cwe"]
        else:
            cve["cwe"] = defaultvalue["cwe"]

        cve["vulnerable_configuration_cpe_2_2"] = []

        return cve

    def process_downloads(self, sites: list = None):
        """
        Method to download and process files
        """

        self.logger.info("Starting download...")

        start_time = time.time()

        self.last_modified = datetime.datetime.now()

        self.logger.debug(
            f"do_process = {self.do_process}; is_update = {self.is_update}"
        )

        if self.do_process:
            if not self.is_update:
                try:
                    total_results = self.api_handler.get_count(
                        self.api_handler.datasource.CVE
                    )
                except ApiMaxRetryError:
                    # failed to get the count; set total_results to 0 and continue
                    total_results = 0

                self.logger.info(f"Preparing to download {total_results} CVE entries")

                with tqdm(
                    desc="Downloading and processing content",
                    total=total_results,
                    position=0,
                    leave=True,
                ) as pbar:
                    for entry in self.api_handler.get_all_data(data_type="cve"):
                        # do something here with the results...
                        for data_list in tqdm(
                            entry, desc=f"Processing batch", leave=False
                        ):
                            if not isinstance(data_list, ApiDataRetrievalFailed):
                                if not isinstance(data_list, Exception):
                                    processed_items = [
                                        self.process_item(item)
                                        for item in data_list["vulnerabilities"]
                                    ]
                                    self._db_bulk_writer(
                                        processed_items, initialization_run=True
                                    )
                                    pbar.update(len(data_list["vulnerabilities"]))
                                else:
                                    self.logger.error(
                                        f"Retrieval of api data resulted in an Exception: {data_list}..."
                                    )
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )
            else:
                last_mod_start_date = self.database[self.feed_type.lower()].find_one(
                    {}, {"lastModified": 1}, sort=[("lastModified", -1)]
                )

                if last_mod_start_date is not None:
                    if "lastModified" in last_mod_start_date:
                        last_mod_start_date = last_mod_start_date["lastModified"]
                    else:
                        raise KeyError(
                            "Missing field 'lastModified' from database query..."
                        )
                else:
                    self.logger.warning(
                        "No records found in the mongodb cves collection.."
                    )
                    return

                    # Get datetime from runtime
                last_mod_end_date = datetime.datetime.now()

                try:
                    total_results = self.api_handler.get_count(
                        self.api_handler.datasource.CVE,
                        last_mod_start_date=last_mod_start_date,
                        last_mod_end_date=last_mod_end_date,
                    )
                except ApiMaxRetryError:
                    # failed to get the count; set total_results to 0 and continue
                    total_results = 0

                self.logger.info(f"Preparing to download {total_results} CVE entries")

                with tqdm(
                    desc="Downloading and processing content",
                    total=total_results,
                    position=0,
                    leave=True,
                ) as pbar:
                    for entry in self.api_handler.get_all_data(
                        data_type="cve",
                        last_mod_start_date=last_mod_start_date,
                        last_mod_end_date=last_mod_end_date,
                    ):
                        # do something here with the results...
                        for data_list in tqdm(
                            entry, desc=f"Processing batch", leave=False
                        ):
                            if not isinstance(data_list, ApiDataRetrievalFailed):
                                if not isinstance(data_list, Exception):
                                    processed_items = [
                                        self.process_item(item)
                                        for item in data_list["vulnerabilities"]
                                    ]
                                    self._db_bulk_writer(processed_items)
                                    pbar.update(len(data_list["vulnerabilities"]))
                                else:
                                    self.logger.error(
                                        f"Retrieval of api data resulted in an Exception: {data_list}..."
                                    )
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )

            # Set the last update time in the info collection
            self.setColUpdate(self.feed_type.lower(), self.last_modified)

        self.logger.info(
            f"Duration: {datetime.timedelta(seconds=time.time() - start_time)}"
        )

    def update(self):
        self.logger.info("CVE database update started")

        self.process_downloads()

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            self.database_indexer.create_indexes(collection=self.feed_type.lower())
            self.is_update = False

        self.logger.info("Finished CVE database update")

        return self.last_modified

    def populate(self):
        self.logger.info("CVE database population started")

        self.logger.info(
            f"Starting CVE database population starting from year: {self.config.CVE_START_YEAR}"
        )

        self.is_update = False

        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        self.process_downloads()

        self.database_indexer.create_indexes(collection=self.feed_type.lower())

        self.logger.info("Finished CVE database population")

        return self.last_modified


class VIADownloads(JSONFileHandler):
    """
    Class processing VIA4 source files
    """

    def __init__(self):
        self.feed_type = "VIA4"
        self.prefix = "cves"
        super().__init__(
            feed_type=self.feed_type, prefix=self.prefix, logger_name=__name__
        )

        self.feed_url = self.config.SOURCES[self.feed_type.lower()]

    def file_to_queue(self, file_tuple: Tuple[str, str]):
        working_dir, filename = file_tuple

        for cve in self.ijson_handler.fetch(filename=filename, prefix=self.prefix):
            x = 0
            for key, val in cve.items():
                entry_dict = {"id": key}
                entry_dict.update(val)
                self.process_item(item=entry_dict)
                x += 1

            self.logger.debug(f"Processed {x} items from file: {filename}")

        with open(filename, "rb") as input_file:
            data = json.loads(input_file.read().decode("utf-8"))

            self.setColInfo("via4", "sources", data["metadata"]["sources"])
            self.setColInfo("via4", "searchables", data["metadata"]["searchables"])

            self.logger.debug(f"Processed metadata from file: {filename}")

        try:
            self.logger.debug(f"Removing working dir: {working_dir}")
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(f"Failed to remove working dir; error produced: {err}")

    def process_item(self, item: dict):
        if self.is_update:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.UpdateOne,
                    doc=item,
                )
            )
        else:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.InsertOne,
                    doc=item,
                )
            )

    def update(self, **kwargs):
        self.logger.info("VIA4 database update started")

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            self.is_update = False

        self.process_downloads([self.feed_url])

        self.logger.info("Finished VIA4 database update")

        return self.last_modified

    def populate(self, **kwargs):
        self.is_update = False
        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        return self.update()


class CAPECDownloads(XMLFileHandler):
    """
    Class processing CAPEC source files
    """

    def __init__(self):
        self.feed_type = "CAPEC"
        super().__init__(feed_type=self.feed_type, logger_name=__name__)

        self.feed_url = self.config.SOURCES[self.feed_type.lower()]

        # make parser
        self.parser = make_parser()
        self.ch = CapecHandler()
        self.parser.setContentHandler(self.ch)

    def file_to_queue(self, file_tuple: Tuple[str, str]):
        working_dir, filename = file_tuple

        self.parser.parse(filename)
        x = 0
        for attack in self.ch.capec:
            self.process_item(attack)
            x += 1

        self.logger.debug(f"Processed {x} entries from file: {filename}")

        try:
            self.logger.debug(f"Removing working dir: {working_dir}")
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(f"Failed to remove working dir; error produced: {err}")

    def update(self, **kwargs):
        self.logger.info("CAPEC database update started")

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            self.is_update = False

        self.process_downloads([self.feed_url])

        self.logger.info("Finished CAPEC database update")

        return self.last_modified

    def populate(self, **kwargs):
        self.is_update = False
        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        return self.update()


class CWEDownloads(XMLFileHandler):
    """
    Class processing CWE source files
    """

    def __init__(self):
        self.feed_type = "CWE"
        super().__init__(feed_type=self.feed_type, logger_name=__name__)

        self.feed_url = self.config.SOURCES[self.feed_type.lower()]

        # make parser
        self.parser = make_parser()
        self.ch = CWEHandler()
        self.parser.setContentHandler(self.ch)

    def file_to_queue(self, file_tuple: Tuple[str, str]):
        working_dir, filename = file_tuple

        for f in glob.glob(f"{working_dir}/*.xml"):
            filename = f

        self.parser.parse(f"file://{filename}")
        x = 0
        for cwe in self.ch.cwe:
            try:
                cwe["related_weaknesses"] = list(set(cwe["related_weaknesses"]))
                cwe["description"] = cwe["Description"]
                cwe.pop("Description")
            except KeyError:
                pass
            self.process_item(cwe)
            x += 1

        self.logger.debug(f"Processed {x} entries from file: {filename}")

        try:
            self.logger.debug(f"Removing working dir: {working_dir}")
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(f"Failed to remove working dir; error produced: {err}")

    def update(self, **kwargs):
        self.logger.info("CWE database update started")

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            self.is_update = False

        self.process_downloads([self.feed_url])

        self.logger.info("Finished CWE database update")

        return self.last_modified

    def populate(self, **kwargs):
        self.is_update = False
        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        return self.update()


class EPSSDownloads(CSVFileHandler):
    def __init__(self):
        self.feed_type = "EPSS"
        self.delimiter = ","
        super().__init__(
            feed_type=self.feed_type, logger_name=__name__, delimiter=self.delimiter
        )

        self.feed_url = self.config.SOURCES[self.feed_type.lower()]

        self.is_update = True

    def process_epss_item(self, item=None):
        if item is None:
            return None

        epss = {
            "id": item[0],
            "epss": item[1],
            "epssMetric": {"percentile": item[2], "lastModified": self.last_modified},
        }

        return epss

    def process_item(self, item):
        epss = self.process_epss_item(item)

        if epss is not None:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.UpdateOne,
                    doc=epss,
                )
            )

    def update(self, **kwargs):
        self.logger.info("EPSS database update started")

        self.queue.clear()

        self.process_downloads([self.feed_url])

        self.logger.info("Finished EPSS database update")

        return self.last_modified

    def populate(self, **kwargs):
        self.logger.info("EPSS Database population started")

        self.queue.clear()

        self.process_downloads([self.feed_url])

        self.logger.info("Finished EPSS database population")

        return self.last_modified
