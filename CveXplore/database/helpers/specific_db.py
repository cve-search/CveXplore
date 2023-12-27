"""
Specific database functions
===========================
"""
import re
from functools import reduce
from typing import List

from pymongo import DESCENDING

from CveXplore.database.helpers.generic_db import GenericDatabaseFactory
from CveXplore.errors.validation import CveNumberValidationError
from CveXplore.objects.cvexplore_object import CveXploreObject


class CvesDatabaseFunctions(GenericDatabaseFactory):
    """
    The CvesDatabaseFunctions is a specific class that provides the cves attribute of a CveXplore instance additional
    functions that only apply to the 'cves' collection
    """

    def __init__(self, collection: str):
        super().__init__(collection)

    def get_cves_for_vendor(
        self, vendor: str, limit: int = 0
    ) -> List[CveXploreObject] | None:
        """
        Function to return cves based on a given vendor. By default, to result is sorted descending on th cvss field.
        """

        the_result = list(
            self.datasource_collection_connection.find({"vendors": vendor})
            .limit(limit)
            .sort("cvss", DESCENDING)
        )

        if len(the_result) != 0:
            return the_result
        else:
            return None

    def __parse_cve_id(self, doc_id: str) -> str:
        # first try to match full cve number format
        reg_match = re.compile(r"[cC][vV][eE]-\d{4}-\d{4,10}")
        if reg_match.match(doc_id) is not None:
            doc_id = doc_id.upper()
        else:
            part_match = re.compile(r"\d{4}-\d{4,10}")
            if part_match.match(doc_id) is not None:
                doc_id = f"CVE-{doc_id}"
            else:
                raise CveNumberValidationError(
                    "Could not validate the CVE number. The number format should be either "
                    "CVE-2000-0001, cve-2000-0001 or 2000-0001."
                )
        return doc_id

    def get_by_id(self, doc_id: str):
        """
        Method to retrieve a single CVE from the database by its CVE ID number.
        The number format should be either CVE-2000-0001, cve-2000-0001 or 2000-0001.
        """
        doc_id = self.__parse_cve_id(doc_id)

        if not isinstance(doc_id, str):
            try:
                doc_id = str(doc_id)
            except ValueError:
                return "Provided value is not a string nor can it be cast to one"

        return self.datasource_collection_connection.find_one({"id": doc_id})

    def _field_list(self, doc_id: str) -> list:
        """
        Method to fetch all field names from a specific collection
        """
        doc_id = self.__parse_cve_id(doc_id)

        return sorted(
            list(
                reduce(
                    lambda all_keys, rec_keys: all_keys | set(rec_keys),
                    map(
                        lambda d: d.to_dict(),
                        [
                            self.datasource_collection_connection.find_one(
                                {"id": doc_id}
                            )
                        ],
                    ),
                    set(),
                )
            )
        )


class CpeDatabaseFunctions(GenericDatabaseFactory):
    """
    The CpeDatabaseFunctions is a specific class that provides the cpe attribute of a CveXplore instance additional
    functions that only apply to the 'cpe' collection
    """

    def __init__(self, collection: str):
        super().__init__(collection)

    def search_active_cpes(
        self, field: str, value: str, limit: int = 0, sorting: int = 1
    ) -> List[CveXploreObject] | None:
        """
        Function to regex search for cpe based on value in string. Only active (deprecated == false) cpe records are
        returned.
        """
        regex = re.compile(value, re.IGNORECASE)

        query = {"$and": [{field: {"$regex": regex}}, {"deprecated": False}]}

        the_result = list(
            self.datasource_collection_connection.find(query)
            .limit(limit)
            .sort(field, sorting)
        )

        if len(the_result) != 0:
            return the_result
        else:
            return None

    def find_active_cpes(
        self, field: str, value: str, limit: int = 0, sorting: int = 1
    ) -> List[CveXploreObject] | None:
        """
        Function to find cpe based on value in string. Only active (deprecated == false) cpe records are
        returned.
        """
        query = {"$and": [{field: value}, {"deprecated": False}]}

        the_result = list(
            self.datasource_collection_connection.find(query)
            .limit(limit)
            .sort(field, sorting)
        )

        if len(the_result) != 0:
            return the_result
        else:
            return None


class CapecDatabaseFunctions(GenericDatabaseFactory):
    """
    The CapecDatabaseFunctions is a specific class that provides the capec attribute of a CveXplore instance additional
    functions that only apply to the 'capec' collection
    """

    def __init__(self, collection: str):
        super().__init__(collection)


class CWEDatabaseFunctions(GenericDatabaseFactory):
    """
    The CWEDatabaseFunctions is a specific class that provides the cwe attribute of a CveXplore instance additional
    functions that only apply to the 'cwe' collection
    """

    def __init__(self, collection: str):
        super().__init__(collection)
