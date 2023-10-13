"""
Specific database functions
===========================
"""
import re
from typing import List

from pymongo import DESCENDING

from CveXplore.database.helpers.generic_db import GenericDatabaseFactory
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
            self._datasource_collection_connection.find({"vendors": vendor})
            .limit(limit)
            .sort("cvss", DESCENDING)
        )

        if len(the_result) != 0:
            return the_result
        else:
            return None

    def __repr__(self):
        """String representation of object"""
        return "<< CvesDatabaseFunctions:{} >>".format(self._collection)


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
            self._datasource_collection_connection.find(query)
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
            self._datasource_collection_connection.find(query)
            .limit(limit)
            .sort(field, sorting)
        )

        if len(the_result) != 0:
            return the_result
        else:
            return None

    def __repr__(self):
        """String representation of object"""
        return "<< CpeDatabaseFunctions:{} >>".format(self._collection)
