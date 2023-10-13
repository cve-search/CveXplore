"""
Main
====
"""
import functools
import json
import os
import re
from collections import defaultdict
from typing import List, Tuple, Union, Iterable

from pymongo import DESCENDING

from CveXplore.api.connection.api_db import ApiDatabaseSource
from CveXplore.common.cpe_converters import from2to3CPE
from CveXplore.common.db_mapping import database_mapping
from CveXplore.database.connection.mongo_db import MongoDBConnection
from CveXplore.database.maintenance.main_updater import MainUpdater
from CveXplore.errors import DatabaseIllegalCollection
from CveXplore.errors.validation import CveNumberValidationError
from CveXplore.objects.cvexplore_object import CveXploreObject

try:
    from version import VERSION
except ModuleNotFoundError:
    _PKG_DIR = os.path.dirname(__file__)
    version_file = os.path.join(_PKG_DIR, "VERSION")
    with open(version_file, "r") as fdsec:
        VERSION = fdsec.read()


class CveXplore(object):
    """
    Main class for CveXplore package
    """

    def __init__(
        self,
        mongodb_connection_details: dict = None,
        api_connection_details: dict = None,
    ):
        """
        Create a new instance of CveXplore

        :param mongodb_connection_details: Provide the connection details needed to establish a connection to a mongodb
                                           instance. The connection details should be in line with pymongo's
                                           documentation.
        :type mongodb_connection_details: dict
        :param api_connection_details: Provide the connection details needed to establish a connection to a cve-search
                                       API provider. The cve-search API provider should allow access to the 'query' POST
                                       endpoint; all other API endpoints are not needed for CveXplore to function. For
                                       the connection details supported please check the :ref:`API connection <api>`
                                       documentation.
        :type api_connection_details: dict
        """
        self.__version = VERSION

        os.environ["DOC_BUILD"] = json.dumps({"DOC_BUILD": "NO"})

        if (
            api_connection_details is not None
            and mongodb_connection_details is not None
        ):
            raise ValueError(
                "CveXplore can be used to connect to either a cve-search database OR a cve-search api, not both!"
            )
        elif api_connection_details is None and mongodb_connection_details is None:
            # by default assume we are talking to a database
            mongodb_connection_details = {}
            os.environ["MONGODB_CON_DETAILS"] = json.dumps(mongodb_connection_details)
            self.datasource = MongoDBConnection(**mongodb_connection_details)
            self.database = MainUpdater(datasource=self.datasource)
        elif mongodb_connection_details is not None:
            os.environ["MONGODB_CON_DETAILS"] = json.dumps(mongodb_connection_details)
            self.datasource = MongoDBConnection(**mongodb_connection_details)
            self.database = MainUpdater(datasource=self.datasource)
        elif api_connection_details is not None:
            api_connection_details["user_agent"] = "CveXplore:{}".format(self.version)
            os.environ["API_CON_DETAILS"] = json.dumps(api_connection_details)
            self.datasource = ApiDatabaseSource(**api_connection_details)

        self.database_mapping = database_mapping

        from CveXplore.database.helpers.generic_db import GenericDatabaseFactory
        from CveXplore.database.helpers.specific_db import (
            CvesDatabaseFunctions,
            CpeDatabaseFunctions,
        )

        for each in self.database_mapping:
            try:
                if each == "cves":
                    setattr(self, each, CvesDatabaseFunctions(collection=each))
                elif each == "cpe":
                    setattr(self, each, CpeDatabaseFunctions(collection=each))
                else:
                    setattr(self, each, GenericDatabaseFactory(collection=each))
            except KeyError:
                # no specific or generic methods configured, skipping
                continue

    def get_single_store_entry(
        self, entry_type: str, dict_filter: dict = None
    ) -> CveXploreObject | None:
        """
        Method to perform a query on a *single* collection in the data source and return a *single* result.

        Which specific store are you querying? Choices are:
            - capec;
            - cpe;
            - cwe;
            - via4;
            - cves;
        """

        if dict_filter is None:
            dict_filter = {}

        entry_type = entry_type.lower()

        if entry_type not in self.database_mapping:
            raise DatabaseIllegalCollection(
                "Illegal collection requested: only {} are allowed!".format(
                    self.database_mapping
                )
            )

        result = getattr(self.datasource, "store_{}".format(entry_type)).find_one(
            dict_filter
        )

        return result

    def get_single_store_entries(
        self, query: Tuple[str, dict], limit: int = 10
    ) -> List[CveXploreObject] | None:
        """
        Method to perform a query on a *single* collection in the data source and return all the results.

        Tuple which contains the entry_type and the dict_filter in a tuple.
            Choices for entry_type:
                - capec;
                - cpe;
                - cwe;
                - via4;
                - cves;
            dict_filter is a dictionary representing a filter according to pymongo documentation.
            example:
                get_single_store_entries(("cwe", {"id": "78"}))
        """
        if not isinstance(query, tuple):
            raise ValueError(
                "Wrong parameter type, received: {} expected: tuple".format(type(query))
            )

        if len(query) != 2:
            raise ValueError(
                "Query parameter does not consist of the expected amount of variables, expected: 2 received: {}".format(
                    len(query)
                )
            )

        entry_type, dict_filter = query

        entry_type = entry_type.lower()

        if entry_type not in self.database_mapping:
            raise DatabaseIllegalCollection(
                "Illegal collection requested: only {} are allowed!".format(
                    self.database_mapping
                )
            )

        results = (
            getattr(self.datasource, "store_{}".format(entry_type))
            .find(dict_filter)
            .limit(limit)
        )

        the_results = list(results)

        if len(the_results) != 0:
            return the_results
        else:
            return None

    def get_multi_store_entries(
        self, *queries: List[Tuple[str, dict]], limit: int = 10
    ) -> List[CveXploreObject] | None:
        """
        Method to perform *multiple* queries on *a single* or *multiple* collections in the data source and return the
        results.

        A list of tuples which contains the entry_type and the dict_filter.
            Choices for entry_type:
                - capec;
                - cpe;
                - cwe;
                - via4;
                - cves;
            dict_filter is a dictionary representing a filter according to pymongo documentation.
            example:
                get_multi_store_entries([("cwe", {"id": "78"}), ("cves", {"id": "CVE-2009-0018"})])
        """

        results = map(
            functools.partial(self.get_single_store_entries, limit=limit), *queries
        )

        joined_list = []

        for result_list in results:
            joined_list += result_list

        the_results = list(joined_list)

        if len(the_results) != 0:
            return the_results
        else:
            return None

    def cves_for_cpe(self, cpe_string: str) -> List[CveXploreObject] | None:
        """
        Method for retrieving Cves that match a single CPE string. By default, the search will be made matching
        the configuration fields of the cves documents.
        CPE string could be formatted like: ``cpe:2.3:o:microsoft:windows_7:*:sp1:*:*:*:*:*:*``
        """

        # format to cpe2.3
        cpe_string = from2to3CPE(cpe_string)

        if cpe_string.startswith("cpe"):
            # strict search with term starting with cpe; e.g: cpe:2.3:o:microsoft:windows_7:*:sp1:*:*:*:*:*:*

            remove_trailing_regex_stars = r"(?:\:|\:\:|\:\*)+$"

            cpe_regex = re.escape(re.sub(remove_trailing_regex_stars, "", cpe_string))

            cpe_regex_string = r"^{}:".format(cpe_regex)
        else:
            # more general search on same field; e.g. microsoft:windows_7
            cpe_regex_string = "{}".format(re.escape(cpe_string))

        cves = self.get_single_store_entries(
            ("cves", {"vulnerable_configuration": {"$regex": cpe_regex_string}}),
            limit=0,
        )

        return cves

    def cve_by_id(self, cve_id: str) -> CveXploreObject | None:
        """
        Method to retrieve a single CVE from the database by its CVE ID number.
        The number format should be either CVE-2000-0001, cve-2000-0001 or 2000-0001.
        """

        # first try to match full cve number format
        reg_match = re.compile(r"[cC][vV][eE]-\d{4}-\d{4,10}")
        if reg_match.match(cve_id) is not None:
            cve_id = cve_id.upper()
        else:
            part_match = re.compile(r"\d{4}-\d{4,10}")
            if part_match.match(cve_id) is not None:
                cve_id = f"CVE-{cve_id}"
            else:
                raise CveNumberValidationError(
                    "Could not validate the CVE number. The number format should be either "
                    "CVE-2000-0001, cve-2000-0001 or 2000-0001."
                )

        return self.get_single_store_entry("cves", {"id": cve_id})

    def cves_by_id(self, *cve_ids: str) -> Union[Iterable[CveXploreObject], Iterable]:
        """
        Method to retrieve a multiple CVE's from the database by its CVE ID number.
        The number format should be either CVE-2000-0001, cve-2000-0001 or 2000-0001.
        """
        ret_data = []
        for cve_id in cve_ids:
            ret_data.append(self.cve_by_id(cve_id=cve_id))

        if len(ret_data) >= 1:
            return sorted(ret_data, key=lambda x: x.id)
        else:
            return ret_data

    def capec_by_cwe_id(self, cwe_id: int) -> List[CveXploreObject] | None:
        """
        Method to retrieve capecs related to a specific CWE ID
        """

        cwe = self.get_single_store_entry("cwe", {"id": cwe_id})

        if cwe is not None:
            return list(cwe.iter_related_capecs())
        else:
            return cwe

    def last_cves(self, limit: int = 10) -> List[CveXploreObject] | None:
        """
        Method to retrieve the last entered / changed cves. By default, limited to 10.
        """

        results = (
            getattr(self.datasource, "store_cves")
            .find()
            .sort("modified", DESCENDING)
            .limit(limit)
        )

        the_results = list(results)

        if len(the_results) != 0:
            return the_results
        else:
            return None

    def get_db_content_stats(self) -> dict | str:
        """
        Property returning the stats from the database. Stats consist of the time last modified and the document count
        per cvedb store in the database.
        """

        stats = defaultdict(dict)

        if not isinstance(self.datasource, ApiDatabaseSource):
            if hasattr(self.datasource, "store_info"):
                results = self.datasource.store_info.find({})
                for each in results:
                    each.pop("_id")
                    db = each["db"]
                    each.pop("db")

                    if "sources" in each:
                        each.pop("sources")
                        each.pop("searchables")

                    each["lastModified"] = str(each["lastModified"])
                    each["document count"] = getattr(
                        self.datasource, "store_{}".format(db)
                    ).count_documents({})
                    stats[db] = each

                    for mgmtlist in ["mgmt_blacklist", "mgmt_whitelist"]:
                        stats[mgmtlist] = {
                            "document count": getattr(
                                self.datasource, "store_{}".format(mgmtlist)
                            ).count_documents({})
                        }

                return dict(stats)

            else:
                return "Database info could not be retrieved"

        return "Using api endpoint: {}".format(self.datasource.baseurl)

    @property
    def version(self):
        """Property returning current version"""
        return self.__version

    def __repr__(self):
        """String representation of object"""
        return "<< CveXplore:{} >>".format(self.version)
