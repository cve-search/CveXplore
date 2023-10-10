"""
Source processing classes
=========================
"""
import datetime
import glob
import hashlib
import json
import logging
import os
import shutil
import time
from collections import namedtuple
from xml.sax import make_parser

import pymongo
from dateutil.parser import parse as parse_datetime
from pymongo import TEXT, ASCENDING
from tqdm import tqdm

from CveXplore.common.config import Configuration
from CveXplore.database.connection.mongo_db import MongoDBConnection
from CveXplore.database.maintenance.Toolkit import generate_title
from CveXplore.database.maintenance.api_handlers import NVDApiHandler
from CveXplore.database.maintenance.content_handlers import CapecHandler, CWEHandler
from CveXplore.database.maintenance.db_action import DatabaseAction
from CveXplore.database.maintenance.file_handlers import XMLFileHandler, JSONFileHandler
from CveXplore.errors.apis import ApiDataRetrievalFailed

date = datetime.datetime.now()
year = date.year + 1

# default config
defaultvalue = {"cwe": "Unknown"}

cveStartYear = Configuration.getCVEStartYear()


class CPEDownloads(NVDApiHandler):
    """
    Class processing CPE source files
    """

    def __init__(self):
        self.feed_type = "CPE"

        super().__init__(self.feed_type)

        self.logger = logging.getLogger("CPEDownloads")

    def file_to_queue(self, *args):
        pass

    @staticmethod
    def process_the_item(item=None):
        if item is None:
            return None

        item = item["cpe"]

        if "cpeName" not in item:
            return None

        title = None

        if "titles" in item:
            for t in item["titles"]:
                if t["lang"] == "en":
                    title = t["title"]

        cpe = {
            "title": title,
            "CveSearchtitle": generate_title(item["cpeName"]),
            "cpe_2_2": item["cpeName"],
            "vendor": item["cpeName"].split(":")[3],
            "product": item["cpeName"].split(":")[4],
            "cpeNameId": item["cpeNameId"],
            "lastModified": parse_datetime(item["lastModified"], ignoretz=True),
            "created": parse_datetime(item["created"], ignoretz=True),
            "deprecated": item["deprecated"],
        }

        version_info = ""
        if "versionStartExcluding" in item:
            cpe["versionStartExcluding"] = item["versionStartExcluding"]
            version_info += cpe["versionStartExcluding"] + "_VSE"
        if "versionStartIncluding" in item:
            cpe["versionStartIncluding"] = item["versionStartIncluding"]
            version_info += cpe["versionStartIncluding"] + "_VSI"
        if "versionEndExcluding" in item:
            cpe["versionEndExcluding"] = item["versionEndExcluding"]
            version_info += cpe["versionEndExcluding"] + "_VEE"
        if "versionEndIncluding" in item:
            cpe["versionEndIncluding"] = item["versionEndIncluding"]
            version_info += cpe["versionEndIncluding"] + "_VEI"

        sha1_hash = hashlib.sha1(
            cpe["cpe_2_2"].encode("utf-8") + version_info.encode("utf-8")
        ).hexdigest()

        cpe["id"] = sha1_hash

        return cpe

    def process_downloads(self, sites=None):
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

                total_results = self.api_handler.get_count(
                    self.api_handler.datasource.CPE
                )

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
                                processed_items = [
                                    self.process_item(item)
                                    for item in data_list["products"]
                                ]
                                self._db_bulk_writer(processed_items)
                                pbar.update(len(data_list["products"]))
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )
            else:
                last_mod_start_date = self.database[self.feed_type.lower()].find_one(
                    {}, {"lastModified": 1}, sort=[("lastModified", -1)]
                )

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

                # Get datetime from runtime
                last_mod_end_date = datetime.datetime.now()

                total_results = self.api_handler.get_count(
                    self.api_handler.datasource.CPE,
                    last_mod_start_date=last_mod_start_date,
                    last_mod_end_date=last_mod_end_date,
                )

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
                                processed_items = [
                                    self.process_item(item)
                                    for item in data_list["products"]
                                ]
                                self._db_bulk_writer(processed_items)
                                pbar.update(len(data_list["products"]))
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )

            # Set the last update time in the info collection
            self.setColUpdate(self.feed_type.lower(), self.last_modified)

        self.logger.info(
            "Duration: {}".format(datetime.timedelta(seconds=time.time() - start_time))
        )

    def update(self, **kwargs):
        self.logger.info("CPE database update started")

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            DatabaseIndexer().create_indexes(collection=self.feed_type.lower())
            self.is_update = False

        self.process_downloads()

        self.logger.info("Finished CPE database update")

        return self.last_modified

    def populate(self, **kwargs):
        self.logger.info("CPE Database population started")

        self.is_update = False

        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        DatabaseIndexer().create_indexes(collection=self.feed_type.lower())

        self.process_downloads()

        self.logger.info("Finished CPE database population")

        return self.last_modified


class CVEDownloads(NVDApiHandler):
    """
    Class processing CVE source files
    """

    def __init__(self):
        self.feed_type = "CVES"

        super().__init__(self.feed_type)

        self.logger = logging.getLogger("CVEDownloads")

    @staticmethod
    def get_cve_year_range():
        """
        Method to fetch the years where we need cve's for
        """
        for a_year in range(cveStartYear, year):
            yield a_year

    @staticmethod
    def get_cpe_info(cpeuri):
        query = {}
        version_info = ""
        if "versionStartExcluding" in cpeuri:
            query["versionStartExcluding"] = cpeuri["versionStartExcluding"]
            version_info += query["versionStartExcluding"] + "_VSE"
        if "versionStartIncluding" in cpeuri:
            query["versionStartIncluding"] = cpeuri["versionStartIncluding"]
            version_info += query["versionStartIncluding"] + "_VSI"
        if "versionEndExcluding" in cpeuri:
            query["versionEndExcluding"] = cpeuri["versionEndExcluding"]
            version_info += query["versionEndExcluding"] + "_VEE"
        if "versionEndIncluding" in cpeuri:
            query["versionEndIncluding"] = cpeuri["versionEndIncluding"]
            version_info += query["versionEndIncluding"] + "_VEI"

        return query, version_info

    @staticmethod
    def add_if_missing(cve, key, value):
        if value not in cve[key]:
            cve[key].append(value)
        return cve

    @staticmethod
    def get_vendor_product(cpeUri):
        vendor = cpeUri.split(":")[3]
        product = cpeUri.split(":")[4]
        return vendor, product

    @staticmethod
    def stem(cpeUri):
        cpeArr = cpeUri.split(":")
        return ":".join(cpeArr[:5])

    def file_to_queue(self, *args):
        pass

    def process_the_item(self, item=None):
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
                    cve["summary"] += " {}".format(description["value"])
                else:
                    cve["summary"] = description["value"]

        if "metrics" in item["cve"]:
            cve["access"] = {}
            cve["impact"] = {}
            if "cvssMetricV3" in item["cve"]["metrics"]:
                cve["impact3"] = {}
                cve["exploitability3"] = {}
                cve["impact3"]["availability"] = item["cve"]["metrics"]["cvssMetricV3"][
                    0
                ]["cvssData"]["availabilityImpact"]
                cve["impact3"]["confidentiality"] = item["cve"]["metrics"][
                    "cvssMetricV3"
                ][0]["cvssData"]["confidentialityImpact"]
                cve["impact3"]["integrity"] = item["cve"]["metrics"]["cvssMetricV3"][0][
                    "cvssData"
                ]["integrityImpact"]
                cve["exploitability3"]["attackvector"] = item["cve"]["metrics"][
                    "cvssMetricV3"
                ][0]["cvssData"]["attackVector"]
                cve["exploitability3"]["attackcomplexity"] = item["cve"]["metrics"][
                    "cvssMetricV3"
                ][0]["cvssData"]["attackComplexity"]
                cve["exploitability3"]["privilegesrequired"] = item["cve"]["metrics"][
                    "cvssMetricV3"
                ][0]["cvssData"]["privilegesRequired"]
                cve["exploitability3"]["userinteraction"] = item["cve"]["metrics"][
                    "cvssMetricV3"
                ][0]["cvssData"]["userInteraction"]
                cve["exploitability3"]["scope"] = item["cve"]["metrics"][
                    "cvssMetricV3"
                ][0]["cvssData"]["scope"]
                cve["cvss3"] = float(
                    item["cve"]["metrics"]["cvssMetricV3"][0]["cvssData"]["baseScore"]
                )
                cve["cvss3Vector"] = item["cve"]["metrics"]["cvssMetricV3"][0][
                    "cvssData"
                ]["vectorString"]
                cve["impactScore3"] = float(
                    item["cve"]["metrics"]["cvssMetricV3"][0]["impactScore"]
                )
                cve["exploitabilityScore3"] = float(
                    item["cve"]["metrics"]["cvssMetricV3"][0]["exploitabilityScore"]
                )
                cve["cvss3Time"] = parse_datetime(
                    item["cve"]["lastModified"], ignoretz=True
                )
                cve["cvss3Type"] = item["cve"]["metrics"]["cvssMetricV3"][0]["type"]
                cve["cvss3Source"] = item["cve"]["metrics"]["cvssMetricV3"][0]["source"]
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
            for cpe in item["cve"]["configurations"][0]["nodes"]:
                if "cpeMatch" in cpe:
                    for cpeuri in cpe["cpeMatch"]:
                        if "criteria" not in cpeuri:
                            continue
                        if cpeuri["vulnerable"]:
                            query, version_info = self.get_cpe_info(cpeuri)
                            if query != {}:
                                query["id"] = hashlib.sha1(
                                    cpeuri["criteria"].encode("utf-8")
                                    + version_info.encode("utf-8")
                                ).hexdigest()
                                cpe_info = self.getCPEVersionInformation(query)
                                if cpe_info:
                                    if cpe_info["cpeMatch"]:
                                        for vulnerable_version in cpe_info["cpeMatch"]:
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_product",
                                                vulnerable_version["criteria"],
                                            )
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_configuration",
                                                vulnerable_version["criteria"],
                                            )
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_configuration_stems",
                                                self.stem(
                                                    vulnerable_version["criteria"]
                                                ),
                                            )
                                            vendor, product = self.get_vendor_product(
                                                vulnerable_version["criteria"]
                                            )
                                            cve = self.add_if_missing(
                                                cve, "vendors", vendor
                                            )
                                            cve = self.add_if_missing(
                                                cve, "products", product
                                            )
                                            cve = self.add_if_missing(
                                                cve,
                                                "vulnerable_product_stems",
                                                self.stem(
                                                    vulnerable_version["criteria"]
                                                ),
                                            )
                                    else:
                                        cve = self.add_if_missing(
                                            cve,
                                            "vulnerable_product",
                                            cpeuri["criteria"],
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
                                        cve = self.add_if_missing(
                                            cve, "vendors", vendor
                                        )
                                        cve = self.add_if_missing(
                                            cve, "products", product
                                        )
                                        cve = self.add_if_missing(
                                            cve,
                                            "vulnerable_product_stems",
                                            self.stem(cpeuri["criteria"]),
                                        )
                            else:
                                # If the cpeMatch did not have any of the version start/end modifiers,
                                # add the CPE string as it is.
                                cve = self.add_if_missing(
                                    cve, "vulnerable_product", cpeuri["criteria"]
                                )
                                cve = self.add_if_missing(
                                    cve, "vulnerable_configuration", cpeuri["criteria"]
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
                if "children" in cpe:
                    for child in cpe["children"]:
                        if "cpeMatch" in child:
                            for cpeuri in child["cpeMatch"]:
                                if "criteria" not in cpeuri:
                                    continue
                                if cpeuri["vulnerable"]:
                                    query, version_info = self.get_cpe_info(cpeuri)
                                    if query != {}:
                                        query["id"] = hashlib.sha1(
                                            cpeuri["criteria"].encode("utf-8")
                                            + version_info.encode("utf-8")
                                        ).hexdigest()
                                        cpe_info = self.getCPEVersionInformation(query)
                                        if cpe_info:
                                            if cpe_info["cpeMatch"]:
                                                for vulnerable_version in cpe_info[
                                                    "cpeMatch"
                                                ]:
                                                    cve = self.add_if_missing(
                                                        cve,
                                                        "vulnerable_product",
                                                        vulnerable_version["criteria"],
                                                    )
                                                    cve = self.add_if_missing(
                                                        cve,
                                                        "vulnerable_configuration",
                                                        vulnerable_version["criteria"],
                                                    )
                                                    cve = self.add_if_missing(
                                                        cve,
                                                        "vulnerable_configuration_stems",
                                                        self.stem(
                                                            vulnerable_version[
                                                                "criteria"
                                                            ]
                                                        ),
                                                    )
                                                    (
                                                        vendor,
                                                        product,
                                                    ) = self.get_vendor_product(
                                                        vulnerable_version["criteria"]
                                                    )
                                                    cve = self.add_if_missing(
                                                        cve, "vendors", vendor
                                                    )
                                                    cve = self.add_if_missing(
                                                        cve, "products", product
                                                    )
                                                    cve = self.add_if_missing(
                                                        cve,
                                                        "vulnerable_product_stems",
                                                        self.stem(
                                                            vulnerable_version[
                                                                "criteria"
                                                            ]
                                                        ),
                                                    )
                                            else:
                                                cve = self.add_if_missing(
                                                    cve,
                                                    "vulnerable_product",
                                                    cpeuri["criteria"],
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
                                                (
                                                    vendor,
                                                    product,
                                                ) = self.get_vendor_product(
                                                    cpeuri["criteria"]
                                                )
                                                cve = self.add_if_missing(
                                                    cve, "vendors", vendor
                                                )
                                                cve = self.add_if_missing(
                                                    cve, "products", product
                                                )
                                                cve = self.add_if_missing(
                                                    cve,
                                                    "vulnerable_product_stems",
                                                    self.stem(cpeuri["criteria"]),
                                                )
                                    else:
                                        # If the cpeMatch did not have any of the version start/end modifiers,
                                        # add the CPE string as it is.
                                        if "criteria" not in cpeuri:
                                            continue
                                        cve = self.add_if_missing(
                                            cve,
                                            "vulnerable_product",
                                            cpeuri["criteria"],
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
                                        cve = self.add_if_missing(
                                            cve, "vendors", vendor
                                        )
                                        cve = self.add_if_missing(
                                            cve, "products", product
                                        )
                                        cve = self.add_if_missing(
                                            cve,
                                            "vulnerable_product_stems",
                                            self.stem(cpeuri["criteria"]),
                                        )
                                else:
                                    if "criteria" not in cpeuri:
                                        continue
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

    def process_downloads(self, sites=None):
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

                total_results = self.api_handler.get_count(
                    self.api_handler.datasource.CVE
                )

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
                                processed_items = [
                                    self.process_item(item)
                                    for item in data_list["vulnerabilities"]
                                ]
                                self._db_bulk_writer(processed_items)
                                pbar.update(len(data_list["vulnerabilities"]))
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )
            else:
                last_mod_start_date = self.database[self.feed_type.lower()].find_one(
                    {}, {"lastModified": 1}, sort=[("lastModified", -1)]
                )

                if "lastModified" in last_mod_start_date:
                    last_mod_start_date = last_mod_start_date["lastModified"]
                else:
                    raise KeyError(
                        "Missing field 'lastModified' from database query..."
                    )

                # Get datetime from runtime
                last_mod_end_date = datetime.datetime.now()

                total_results = self.api_handler.get_count(
                    self.api_handler.datasource.CVE,
                    last_mod_start_date=last_mod_start_date,
                    last_mod_end_date=last_mod_end_date,
                )

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
                                processed_items = [
                                    self.process_item(item)
                                    for item in data_list["vulnerabilities"]
                                ]
                                self._db_bulk_writer(processed_items)
                                pbar.update(len(data_list["vulnerabilities"]))
                            else:
                                self.logger.error(
                                    f"Retrieval of api data on url: {data_list.args[0]} failed...."
                                )

            # Set the last update time in the info collection
            self.setColUpdate(self.feed_type.lower(), self.last_modified)

        self.logger.info(
            "Duration: {}".format(datetime.timedelta(seconds=time.time() - start_time))
        )

    def update(self):
        self.logger.info("CVE database update started")

        # if collection is non-existent; assume it's not an update
        if self.feed_type.lower() not in self.getTableNames():
            DatabaseIndexer().create_indexes(collection=self.feed_type.lower())
            self.is_update = False

        self.process_downloads()

        self.logger.info("Finished CVE database update")

        return self.last_modified

    def populate(self):

        self.logger.info("CVE database population started")

        self.logger.info(
            "Starting CVE database population starting from year: {}".format(
                cveStartYear
            )
        )

        self.is_update = False

        self.queue.clear()

        self.delColInfo(self.feed_type.lower())

        self.dropCollection(self.feed_type.lower())

        DatabaseIndexer().create_indexes(collection=self.feed_type.lower())

        self.process_downloads()

        self.logger.info("Finished CVE database population")

        return self.last_modified


class VIADownloads(JSONFileHandler):
    """
    Class processing VIA4 source files
    """

    def __init__(self):
        self.feed_type = "VIA4"
        self.prefix = "cves"
        super().__init__(self.feed_type, self.prefix)

        self.feed_url = Configuration.getFeedURL(self.feed_type.lower())

        self.logger = logging.getLogger("VIADownloads")

    def file_to_queue(self, file_tuple):

        working_dir, filename = file_tuple

        for cve in self.ijson_handler.fetch(filename=filename, prefix=self.prefix):
            x = 0
            for key, val in cve.items():
                entry_dict = {"id": key}
                entry_dict.update(val)
                self.process_item(item=entry_dict)
                x += 1

            self.logger.debug("Processed {} items from file: {}".format(x, filename))

        with open(filename, "rb") as input_file:
            data = json.loads(input_file.read().decode("utf-8"))

            self.setColInfo("via4", "sources", data["metadata"]["sources"])
            self.setColInfo("via4", "searchables", data["metadata"]["searchables"])

            self.logger.debug("Processed metadata from file: {}".format(filename))

        try:
            self.logger.debug("Removing working dir: {}".format(working_dir))
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(
                "Failed to remove working dir; error produced: {}".format(err)
            )

    def process_item(self, item):

        if self.is_update:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.UpdateOne,
                    collection=self.feed_type.lower(),
                    doc=item,
                )
            )
        else:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.InsertOne,
                    collection=self.feed_type.lower(),
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
        super().__init__(self.feed_type)

        self.feed_url = Configuration.getFeedURL(self.feed_type.lower())

        self.logger = logging.getLogger("CAPECDownloads")

        # make parser
        self.parser = make_parser()
        self.ch = CapecHandler()
        self.parser.setContentHandler(self.ch)

    def file_to_queue(self, file_tuple):

        working_dir, filename = file_tuple

        self.parser.parse(filename)
        x = 0
        for attack in self.ch.capec:
            self.process_item(attack)
            x += 1

        self.logger.debug("Processed {} entries from file: {}".format(x, filename))

        try:
            self.logger.debug("Removing working dir: {}".format(working_dir))
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(
                "Failed to remove working dir; error produced: {}".format(err)
            )

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
        super().__init__(self.feed_type)

        self.feed_url = Configuration.getFeedURL(self.feed_type.lower())

        self.logger = logging.getLogger("CWEDownloads")

        # make parser
        self.parser = make_parser()
        self.ch = CWEHandler()
        self.parser.setContentHandler(self.ch)

    def file_to_queue(self, file_tuple):

        working_dir, filename = file_tuple

        for f in glob.glob(f"{working_dir}/*.xml"):
            filename = f

        self.parser.parse(f"file://{filename}")
        x = 0
        for cwe in self.ch.cwe:
            try:
                cwe["related_weaknesses"] = list(set(cwe["related_weaknesses"]))
            except KeyError:
                pass
            self.process_item(cwe)
            x += 1

        self.logger.debug("Processed {} entries from file: {}".format(x, filename))

        try:
            self.logger.debug("Removing working dir: {}".format(working_dir))
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(
                "Failed to remove working dir; error produced: {}".format(err)
            )

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


MongoUniqueIndex = namedtuple("MongoUniqueIndex", "index name unique")
MongoAddIndex = namedtuple("MongoAddIndex", "index name")


class DatabaseIndexer(object):
    """
    Class processing the Mongodb indexes
    """

    def __init__(self):

        database = MongoDBConnection(**json.loads(os.getenv("MONGODB_CON_DETAILS")))
        self.database = database._dbclient

        self.indexes = {
            "cpe": [
                MongoUniqueIndex(index=[("id", ASCENDING)], name="id", unique=True),
                MongoAddIndex(index=[("vendor", ASCENDING)], name="vendor"),
                MongoAddIndex(index=[("product", ASCENDING)], name="product"),
            ],
            "cpeother": [
                MongoUniqueIndex(index=[("id", ASCENDING)], name="id", unique=True)
            ],
            "cves": [
                MongoAddIndex(index=[("id", ASCENDING)], name="id"),
                MongoAddIndex(
                    index=[("vulnerable_configuration", ASCENDING)],
                    name="vulnerable_configuration",
                ),
                MongoAddIndex(
                    index=[("vulnerable_product", ASCENDING)], name="vulnerable_product"
                ),
                MongoAddIndex(index=[("modified", ASCENDING)], name="modified"),
                MongoAddIndex(index=[("published", ASCENDING)], name="published"),
                MongoAddIndex(index=[("lastModified", ASCENDING)], name="lastModified"),
                MongoAddIndex(index=[("cvss", ASCENDING)], name="cvss"),
                MongoAddIndex(index=[("cvss3", ASCENDING)], name="cvss3"),
                MongoAddIndex(index=[("summary", TEXT)], name="summary"),
                MongoAddIndex(index=[("vendors", ASCENDING)], name="vendors"),
                MongoAddIndex(index=[("products", ASCENDING)], name="products"),
                MongoAddIndex(
                    index=[("vulnerable_product_stems", ASCENDING)],
                    name="vulnerable_product_stems",
                ),
                MongoAddIndex(
                    index=[("vulnerable_configuration_stems", ASCENDING)],
                    name="vulnerable_configuration_stems",
                ),
            ],
            "via4": [MongoAddIndex(index=[("id", ASCENDING)], name="id")],
            "mgmt_whitelist": [MongoAddIndex(index=[("id", ASCENDING)], name="id")],
            "mgmt_blacklist": [MongoAddIndex(index=[("id", ASCENDING)], name="id")],
            "capec": [
                MongoAddIndex(
                    index=[("related_weakness", ASCENDING)], name="related_weakness"
                )
            ],
        }

        self.logger = logging.getLogger("DatabaseIndexer")

    def getInfo(self, collection):
        return self.sanitize(self.database["info"].find_one({"db": collection}))

    def sanitize(self, x):
        if type(x) == pymongo.cursor.Cursor:
            x = list(x)
        if type(x) == list:
            for y in x:
                self.sanitize(y)
        if x and "_id" in x:
            x.pop("_id")
        return x

    def create_indexes(self, collection=None):

        if collection is not None:
            try:
                for each in self.indexes[collection]:
                    if isinstance(each, MongoUniqueIndex):
                        self.setIndex(
                            collection, each.index, name=each.name, unique=each.unique
                        )
                    elif isinstance(each, MongoAddIndex):
                        self.setIndex(collection, each.index, name=each.name)
            except KeyError:
                # no specific index given, continue
                self.logger.warning(
                    "Could not find the requested collection: {}, skipping...".format(
                        collection
                    )
                )
                pass

        else:
            for index in self.iter_indexes():
                self.setIndex(index[0], index[1])

            for collection in self.indexes.keys():
                for each in self.indexes[collection]:
                    if isinstance(each, MongoUniqueIndex):
                        self.setIndex(
                            collection, each.index, name=each.name, unique=each.unique
                        )
                    elif isinstance(each, MongoAddIndex):
                        self.setIndex(collection, each.index, name=each.name)

    def iter_indexes(self):
        for each in self.get_via4_indexes():
            yield each

    def get_via4_indexes(self):
        via4 = self.getInfo("via4")
        result = []
        if via4:
            for index in via4.get("searchables", []):
                result.append(("via4", index))
        return result

    def setIndex(self, col, field, **kwargs):
        try:
            self.database[col].create_index(field, **kwargs)
            self.logger.info("Success to create index %s on %s" % (field, col))
        except Exception as e:
            self.logger.error("Failed to create index %s on %s: %s" % (col, field, e))
