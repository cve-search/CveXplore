import os
import shutil

from dotenv import load_dotenv

if not os.path.exists(os.path.expanduser("~/.cvexplore")):
    os.mkdir(os.path.expanduser("~/.cvexplore"))

user_wd = os.path.expanduser("~/.cvexplore")

if not os.path.exists(os.path.join(user_wd, ".env")):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), "common/.env_example"),
        os.path.join(user_wd, ".env"),
    )

load_dotenv(os.path.join(user_wd, ".env"))

if not os.path.exists(os.path.join(user_wd, ".sources.ini")):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), "common/.sources.ini"),
        os.path.join(user_wd, ".sources.ini"),
    )

import functools
import json
import logging

import re
import warnings
from collections import defaultdict
from typing import List, Tuple, Union, Iterable, Type

from pymongo import DESCENDING

from CveXplore.api.connection.api_db import ApiDatabaseSource
from CveXplore.common.config import Configuration
from CveXplore.common.cpe_converters import create_cpe_regex_string
from CveXplore.common.db_mapping import database_mapping
from CveXplore.core.database_maintenance.main_updater import MainUpdater
from CveXplore.core.general.datasources import supported_datasources
from CveXplore.database.connection.database_connection import DatabaseConnection
from CveXplore.errors import DatabaseIllegalCollection
from CveXplore.errors.datasource import UnsupportedDatasourceException
from CveXplore.errors.validation import CveNumberValidationError
from CveXplore.objects.cvexplore_object import CveXploreObject

try:
    from CveXplore.core.celery_task_handler.task_handler import TaskHandler
except ModuleNotFoundError:
    # This is not a problem, because using the Celery backend is optional.
    # This exception will be handled when loading the TaskHandler fails with
    # a NameError, because we already have logging available there.
    pass


def _version():
    _PKG_DIR = os.path.dirname(__file__)
    version_file = os.path.join(_PKG_DIR, "VERSION")
    with open(version_file, "r") as fdsec:
        VERSION = fdsec.read()

    return VERSION


VERSION = __version__ = _version()


class CveXplore(object):
    """
    The CveXplore class is the main entry point for CveXplore. All functionality is available from straight from this
    class or via the different subclasses / attributes.

    Group:
        Main
    """

    def __init__(self, **kwargs):
        """
        Create a new instance of CveXplore

        Examples:

            >>> from CveXplore import CveXplore
            >>> cvx = CveXplore(datasource_type="mongodb", datasource_connection_details={"host": "mongodb://127.0.0.1:27017"})
            >>> cvx.version
            '0.1.2'

            >>> from CveXplore import CveXplore
            >>> cvx = CveXplore(datasource_type="api", datasource_connection_details={"address": ("mylocal.cve-search.int", 443), "api_path": "api"})
            >>> cvx.version
            '0.1.2'

        Args:
            kwargs['datasource_type']: Which datasource to query.
            kwargs['datasource_connection_details']: Provide the connection details needed to establish a connection \
            to the datasource. The connection details should be in line with the datasource's documentation.

        """
        self.__version = VERSION
        self._config = Configuration
        self.logger = logging.getLogger(__name__)

        # adjust self.config with kwargs parameters; lower case parameters are converted to uppercase and then changed
        # in the self.config object
        for each in kwargs:
            setattr(self.config, each.upper(), kwargs[each])

        self._datasource_type = self.config.DATASOURCE_TYPE

        self._datasource_connection_details = self.config.DATASOURCE_CONNECTION_DETAILS

        self._mongodb_connection_details = self.config.MONGODB_CONNECTION_DETAILS
        self._api_connection_details = self.config.API_CONNECTION_DETAILS

        os.environ["DOC_BUILD"] = json.dumps({"DOC_BUILD": "NO"})

        self.logger.info(
            f"Using {self.datasource_type} as datasource, connection details: {self.datasource_connection_details}"
        )

        if self.datasource_type not in supported_datasources:
            raise UnsupportedDatasourceException(
                f"Unsupported datasource selected: '{self.datasource_type}'; currently supported: {supported_datasources}"
            )

        if self.datasource_type == "api" and self.datasource_connection_details is None:
            raise ValueError(
                "Missing datasource_connection_details for selected datasource ('api')"
            )
        elif self.datasource_type == "api":
            self.datasource_connection_details["user_agent"] = (
                f"CveXplore:{self.version}"
            )

        if (
            self.mongodb_connection_details is not None
            and self.datasource_type == "mongodb"
        ):
            self.logger.warning(
                "The use of mongodb_connection_details is deprecated and will be removed in the 0.4 release, please "
                "use datasource_connection_details instead"
            )
            self._datasource_connection_details = self.mongodb_connection_details
        elif self.api_connection_details is not None and self.datasource_type == "api":
            self.logger.warning(
                "The use of api_connection_details is deprecated and will be removed in the 0.4 release, please "
                "use datasource_connection_details instead"
            )
            self._datasource_connection_details = self.api_connection_details
        else:
            if self.datasource_type == "mongodb":
                self._datasource_connection_details = {
                    "host": (
                        f"{self.config.DATASOURCE_PROTOCOL}://{self.config.DATASOURCE_HOST}:{self.config.DATASOURCE_PORT}"
                        if self.config.DATASOURCE_USER is None
                        and self.config.DATASOURCE_PASSWORD is None
                        else f"{self.config.DATASOURCE_PROTOCOL}://{self.config.DATASOURCE_USER}:{self.config.DATASOURCE_PASSWORD}@{self.config.DATASOURCE_HOST}:{self.config.DATASOURCE_PORT}"
                    ),
                    "database": self.config.DATASOURCE_DBNAME,
                }
            elif self.datasource_type == "mysql":
                self._datasource_connection_details = {
                    "sql_uri": self.config.SQLALCHEMY_DATABASE_URI
                }
            elif self.datasource_type == "api":
                self._datasource_connection_details = {
                    "address": (
                        f"{self.config.DATASOURCE_HOST}",
                        int(f"{self.config.DATASOURCE_PORT}"),
                    ),
                    "api_path": "api",
                }

        setattr(
            self.config,
            "DATASOURCE_CONNECTION_DETAILS",
            self.datasource_connection_details,
        )

        self.datasource = DatabaseConnection(
            database_type=self.datasource_type,
            database_init_parameters=self.datasource_connection_details,
        ).database_connection
        if self.datasource_type != "api":
            self.database = MainUpdater(
                datasource=self.datasource, datasource_type=self.datasource_type
            )

        self._database_mapping = database_mapping

        from CveXplore.database.helpers.specific_db import (
            CvesDatabaseFunctions,
            CpeDatabaseFunctions,
            CapecDatabaseFunctions,
            CWEDatabaseFunctions,
        )

        self.cves = CvesDatabaseFunctions(collection="cves")
        self.cpe = CpeDatabaseFunctions(collection="cpe")
        self.capec = CapecDatabaseFunctions(collection="capec")
        self.cwe = CWEDatabaseFunctions(collection="cwe")

        try:
            self.task_handler = TaskHandler()
        except NameError:
            self.logger.info(
                "Failed to load Celery TaskHandler; "
                "continuing without the optional Celery backend."
            )

        self.logger.info(f"Initialized CveXplore version: {self.version}")

    @property
    def config(self) -> Type[Configuration]:
        """
        Returns Configuration object

        Group:
            Properties
        """
        return self._config

    @property
    def datasource_type(self) -> str:
        """
        Returns Datasource type

        Group:
            Properties
        """
        return self._datasource_type

    @property
    def datasource_connection_details(self) -> dict:
        """
        Returns Datasource Connection Details

        Group:
            Properties
        """
        return self._datasource_connection_details

    @property
    def database_mapping(self) -> dict:
        """
        Returns database mapping

        Group:
            Properties
        """
        return self._database_mapping

    @property
    def mongodb_connection_details(self) -> dict:
        """
        Returns Mongodb Connection Details

        Group:
            Properties
        """
        warnings.warn(
            "The use of mongodb_connection_details is deprecated and will be removed in the 0.4 release, "
            "please use datasource_connection_details instead",
            DeprecationWarning,
        )
        return self._mongodb_connection_details

    @property
    def api_connection_details(self) -> dict:
        """
        Returns Api Connection Details

        Group:
            Properties
        """
        warnings.warn(
            "The use of api_connection_details is deprecated and will be removed in the 0.4 release, please "
            "use datasource_connection_details instead",
            DeprecationWarning,
        )
        return self._api_connection_details

    @property
    def version(self) -> str:
        """
        Returns CveXplore version

        Group:
            Properties
        """
        return self.__version

    @staticmethod
    def where() -> str:
        """
        Request the path where CveXplore is installed

        Returns:
            Path where CveXplore is installed
        """
        return os.path.dirname(__file__)

    def get_single_store_entry(
        self, entry_type: str, dict_filter: dict = None
    ) -> CveXploreObject | None:
        """
        Method to perform a query on a *single* collection in the data source and return a *single* result.

        Examples:

            >>> from CveXplore import CveXplore
            >>> cvx = CveXplore()
            >>> result = cvx.get_single_store_entry("capec", {"id": "1"})
            >>> result
            << Capec:1 >>

        Args:
            entry_type: Which specific store are you querying? Choices are:

                                - capec;
                                - cpe;
                                - cwe;
                                - via4;
                                - cves;
            dict_filter: a dictionary representing a filter according to pymongo documentation

        Returns:
            An instance of CveXploreObject or None
        """

        if dict_filter is None:
            dict_filter = {}

        entry_type = entry_type.lower()

        if entry_type not in self.database_mapping:
            raise DatabaseIllegalCollection(
                f"Illegal collection requested: only {self.database_mapping} are allowed!"
            )

        result = getattr(self.datasource, f"store_{entry_type}").find_one(dict_filter)

        return result

    def get_single_store_entries(
        self, query: Tuple[str, dict], limit: int = 10
    ) -> List[CveXploreObject] | None:
        """
        Method to perform a query on a *single* collection in the data source and return all the results.

        Examples:

           >>> from CveXplore import CveXplore
           >>> cvx = CveXplore()
           >>> result = cvx.get_single_store_entries(("cves", {"cvss": {"$eq": 8}}))
           >>> result
           [<< Cves:CVE-2011-0387 >>,
           << Cves:CVE-2015-1935 >>,
           << Cves:CVE-2014-3053 >>,
           << Cves:CVE-2010-4031 >>,
           << Cves:CVE-2016-1338 >>,
           << Cves:CVE-2013-3633 >>,
           << Cves:CVE-2017-14444 >>,
           << Cves:CVE-2017-14446 >>,
           << Cves:CVE-2017-14445 >>,
           << Cves:CVE-2016-2354 >>]

           >>> from CveXplore import CveXplore
           >>> cvx = CveXplore()
           >>> result = cvx.get_single_store_entries(("cves", {"cvss": {"$eq": 8}}), limit=0)
           >>> len(result)
           32

        Args:
            query: Tuple which contains the entry_type and the dict_filter in a tuple. Choices for entry_type:

                        - capec;
                        - cpe;
                        - cwe;
                        - via4;
                        - cves;

                    dict_filter is a dictionary representing a filter according to pymongo documentation.
            limit: Limit the number of results to return.

        Returns:
            A list with CveXploreObject's or None
        """
        if not isinstance(query, tuple):
            raise ValueError(
                f"Wrong parameter type, received: {type(query)} expected: tuple"
            )

        if len(query) != 2:
            raise ValueError(
                f"Query parameter does not consist of the expected amount of variables, "
                f"expected: 2 received: {len(query)}"
            )

        entry_type, dict_filter = query

        entry_type = entry_type.lower()

        if entry_type not in self.database_mapping:
            raise DatabaseIllegalCollection(
                f"Illegal collection requested: only {self.database_mapping} are allowed!"
            )

        if entry_type == "cves":
            if "id" in dict_filter:
                if isinstance(dict_filter["id"], str):
                    dict_filter["id"] = self._validate_cve_id(dict_filter["id"])
                elif isinstance(dict_filter["id"], dict):
                    if "$in" in dict_filter["id"]:
                        dict_filter["id"]["$in"] = [
                            self._validate_cve_id(x) for x in dict_filter["id"]["$in"]
                        ]
            if "cvss" in dict_filter:
                if isinstance(dict_filter["cvss"], str):
                    dict_filter["cvss"] = float(dict_filter["cvss"])
            if "cvss3" in dict_filter:
                if isinstance(dict_filter["cvss3"], str):
                    dict_filter["cvss3"] = float(dict_filter["cvss3"])

            if "exploitabilityScore" in dict_filter:
                if isinstance(dict_filter["exploitabilityScore"], str):
                    dict_filter["exploitabilityScore"] = float(
                        dict_filter["exploitabilityScore"]
                    )
            if "exploitabilityScore3" in dict_filter:
                if isinstance(dict_filter["exploitabilityScore3"], str):
                    dict_filter["exploitabilityScore3"] = float(
                        dict_filter["exploitabilityScore3"]
                    )

            if "impactScore" in dict_filter:
                if isinstance(dict_filter["impactScore"], str):
                    dict_filter["impactScore"] = float(dict_filter["impactScore"])
            if "impactScore3" in dict_filter:
                if isinstance(dict_filter["impactScore3"], str):
                    dict_filter["impactScore3"] = float(dict_filter["impactScore3"])

            if "epss" in dict_filter:
                if isinstance(dict_filter["epss"], str):
                    dict_filter["epss"] = float(dict_filter["epss"])

        results = (
            getattr(self.datasource, f"store_{entry_type}")
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

        Examples:

            >>> from CveXplore import CveXplore
            >>> cvx = CveXplore()
            >>> result = cvx.get_multi_store_entries([("CWE", {"id": "78"}), ("cves", {"id": "CVE-2009-0018"})])
            >>> result
            [<< Cwe:78 >>, << Cves:CVE-2009-0018 >>]

        Args:
            queries: A list of tuples which contains the entry_type and the dict_filter. Choices for entry_type:

                    - capec;
                    - cpe;
                    - cwe;
                    - via4;
                    - cves;

                    dict_filter is a dictionary representing a filter according to pymongo documentation.
            limit: Limit the number of results to return.

        Returns:
            A list with CveXploreObject's or None
        """

        results = map(
            functools.partial(self.get_single_store_entries, limit=limit), *queries
        )

        the_results = [
            result_list for result_list in results if result_list is not None
        ]

        # flatten results
        the_results = [item for row in the_results for item in row]

        if len(the_results) != 0:
            return the_results
        else:
            return None

    def cves_for_cpe(self, cpe_string: str) -> List[CveXploreObject] | None:
        """
        Method for retrieving Cves that match a single CPE string. By default, the search will be made matching
        the configuration fields of the cves documents.

        Examples:

            >>> from CveXplore import CveXplore
            >>> cvx = CveXplore()
            >>> cves = cvx.cves_for_cpe("cpe:2.3:o:microsoft:windows_7:*:sp1:*:*:*:*:*:*")

        Args:
            cpe_string: CPE string to search for.

        Returns:
            A list with CveXploreObject's or None
        """

        cpe_regex_string = create_cpe_regex_string(cpe_string)

        cves = self.get_single_store_entries(
            ("cves", {"vulnerable_configuration": {"$regex": cpe_regex_string}}),
            limit=0,
        )

        return cves

    def _validate_cve_id(self, cve_id: str) -> str:
        """
        Method for validating a CVE ID.

        Args:
            cve_id: The CVE ID to validate.

        Returns:
            A validated CVE ID.
        """
        reg_match = re.compile(r"[cC][vV][eE]-\d{4}-\d{4,10}")
        if reg_match.match(cve_id) is not None:
            cve_id = cve_id.upper()
        else:
            part_match = re.compile(r"\d{4}-\d{4,10}")
            if part_match.match(cve_id) is not None:
                cve_id = f"CVE-{cve_id}"
            else:
                raise CveNumberValidationError(
                    f"Could not validate the CVE number: {cve_id}. The number format should be either "
                    "CVE-2000-0001, cve-2000-0001 or 2000-0001."
                )

        return cve_id

    def cve_by_id(self, cve_id: str) -> CveXploreObject | None:
        """
        Method to retrieve a single CVE from the database by its CVE ID number.

        Args:
            cve_id: The number format should be either CVE-2000-0001, cve-2000-0001 or 2000-0001.

        Returns:
            A CveXploreObject or None
        """
        cve_id = self._validate_cve_id(cve_id=cve_id)

        return self.get_single_store_entry("cves", {"id": cve_id})

    def cves_by_id(self, *cve_ids: str) -> Union[Iterable[CveXploreObject], Iterable]:
        """
        Method to retrieve multiple CVE's from the database by their CVE ID numbers.

        Args:
            cve_ids: The number format should be either CVE-2000-0001, cve-2000-0001 or 2000-0001.

        Returns:
            A list with CveXploreObject's or empty list
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
        Method to retrieve CAPEC's related to a specific CWE ID

        Args:
            cwe_id: The CWE ID to retrieve CAPEC for.

        Returns:
            A list with CveXploreObject's or None
        """
        cwe = self.get_single_store_entry("cwe", {"id": cwe_id})

        if cwe is not None:
            return list(cwe.iter_related_capecs())
        else:
            return cwe

    def last_cves(self, limit: int = 10) -> List[CveXploreObject] | None:
        """
        Method to retrieve the last entered / changed cves.

        Args:
            limit: The amount of results to return; defaults to 10.

        Returns:
            A list with CveXploreObject's or None
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
        This method request the statistics from the database and consist of the time last modified and the document count
        per cvedb store in the database.

        Returns:
            The stats from the database.
        """
        stats = defaultdict(dict)

        if not isinstance(self.datasource, ApiDatabaseSource):
            if hasattr(self.datasource, "store_info"):
                results = self.datasource.store_info.find({})
                for each in results:
                    each.pop("_id")
                    db = each["db"]
                    if db == "epss":
                        continue

                    each.pop("db")

                    if "sources" in each:
                        each.pop("sources")
                        each.pop("searchables")

                    each["lastModified"] = str(each["lastModified"])
                    each["document count"] = getattr(
                        self.datasource, f"store_{db}"
                    ).count_documents({})
                    stats[db] = each

                    for mgmtlist in ["mgmt_blacklist", "mgmt_whitelist"]:
                        stats[mgmtlist] = {
                            "document count": getattr(
                                self.datasource, f"store_{mgmtlist}"
                            ).count_documents({})
                        }

                return dict(stats)

            else:
                return "Database info could not be retrieved"

        return f"Using api endpoint: {self.datasource.baseurl}"

    def __repr__(self) -> str:
        """
        String representation of object

        Returns:
            String representation of object
        """
        return f"<< CveXplore:{self.version} >>"
