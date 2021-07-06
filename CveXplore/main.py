"""
Main
====
"""
import functools
import json
import os
import re
from collections import defaultdict

from pymongo import DESCENDING

from CveXplore.api.connection.api_db import ApiDatabaseSource
from CveXplore.common.cpe_converters import from2to3CPE
from CveXplore.common.db_mapping import database_mapping
from CveXplore.database.connection.mongo_db import MongoDBConnection
from CveXplore.errors import DatabaseIllegalCollection
from CveXplore.database.maintenance.main_updater import MainUpdater

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

    def __init__(self, mongodb_connection_details=None, api_connection_details=None):
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
        from CveXplore.database.helpers.specific_db import CvesDatabaseFunctions

        for each in self.database_mapping:
            if each != "cves":
                setattr(self, each, GenericDatabaseFactory(collection=each))
            else:
                setattr(self, each, CvesDatabaseFunctions(collection=each))

    def get_single_store_entry(self, entry_type, dict_filter={}):
        """
        Method to perform a query on a *single* collection in the data source and return a *single* result.

        :param entry_type: Which specific store are you querying? Choices are:
                           - capec;
                           - cpe;
                           - cwe;
                           - via4;
                           - cves;
        :type entry_type: str
        :param dict_filter: Dictionary representing a filter according to pymongo documentation
        :type dict_filter: dict
        :return: Objectified result from the query
        :rtype: object
        """

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

    def get_single_store_entries(self, query, limit=10):
        """
        Method to perform a query on a *single* collection in the data source and return all of the results.

        :param query: Tuple which contains the entry_type and the dict_filter in a tuple.
                      Choices for entry_type:
                      - capec;
                      - cpe;
                      - cwe;
                      - via4;
                      - cves;
                      dict_filter is a dictionary representing a filter according to pymongo documentation.
                      example:
                      get_single_store_entries(("CWE", {"id": "78"}))
        :type query: tuple
        :param limit: Limit the amount of returned results, defaults to 10
        :type limit: int
        :return: list with queried results
        :rtype: list
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

        return list(results)

    def get_multi_store_entries(self, *queries, limit=10):
        """
        Method to perform *multiple* queries on *a single* or *multiple* collections in the data source and return the
        results.

        :param queries: A list of tuples which contains the entry_type and the dict_filter.
                        Choices for entry_type:
                        - capec;
                        - cpe;
                        - cwe;
                        - via4;
                        - cves;
                        dict_filter is a dictionary representing a filter according to pymongo documentation.
                        example:
                        get_multi_store_entries([("CWE", {"id": "78"}), ("cves", {"id": "CVE-2009-0018"})])
        :type queries: list
        :return: Queried results in a single list
        :rtype: list
        """

        results = map(
            functools.partial(self.get_single_store_entries, limit=limit), *queries
        )

        joined_list = []

        for result_list in results:

            joined_list += result_list

        return list(joined_list)

    def cves_for_cpe(self, cpe_string):
        """
        Method for retrieving Cves that match a single CPE string. By default the search will be made matching
        the configuration fields of the cves documents.

        :param cpe_string: CPE string: e.g. ``cpe:2.3:o:microsoft:windows_7:*:sp1:*:*:*:*:*:*``
        :type cpe_string: str
        :return: List with Cves
        :rtype: list
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

    def cve_by_id(self, cve_id):
        """
        Method to retrieve a single CVE from the database by it's CVE ID number

        :param cve_id: String representing the CVE id; e.g. CVE-2020-0001
        :type cve_id: str
        :return: CVE object
        :rtype: Cves
        """
        return self.get_single_store_entry("cves", {"id": cve_id})

    def capec_by_cwe_id(self, cwe_id):
        """
        Method to retrieve capecs related to a specific CWE ID

        :param cwe_id: String representing the CWE id; e.g. '15'
        :type cwe_id:
        :return: List with Capecs
        :rtype: list
        """

        cwe = self.get_single_store_entry("cwe", {"id": cwe_id})

        if cwe is not None:
            return list(cwe.iter_related_capecs())
        else:
            return cwe

    def last_cves(self, limit=10):
        """
        Method to retrieve the last entered / changed cves. By default limited to 10.

        :return: List with Cves
        :rtype: list
        """

        results = (
            getattr(self.datasource, "store_cves")
            .find()
            .sort("Modified", DESCENDING)
            .limit(limit)
        )

        return list(results)

    def get_db_content_stats(self):
        """
        Property returning the stats from the database. Stats consist of the time last modified and the document count
        per cvedb store in the database.

        :return: Statistics
        :rtype: dict
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

                    each["last-modified"] = str(each["last-modified"])
                    each["document count"] = getattr(
                        self.datasource, "store_{}".format(db)
                    ).count()
                    stats[db] = each

                    for mgmtlist in ["mgmt_blacklist", "mgmt_whitelist"]:
                        stats[mgmtlist] = {
                            "document count": getattr(
                                self.datasource, "store_{}".format(mgmtlist)
                            ).count()
                        }

                return dict(stats)

            else:
                return "Database info could not be retrieved"

        return "Using api endpoint: {}".format(self.datasource.url)

    @property
    def version(self):
        """ Property returning current version """
        return self.__version

    def __repr__(self):
        """ String representation of object """
        return "<< CveXplore:{} >>".format(self.version)
