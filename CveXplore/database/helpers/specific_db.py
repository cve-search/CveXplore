"""
Specific database functions
===========================
"""
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

        :param vendor: A vendor to search for; e.g. microsoft
        :type vendor: str
        :param limit: Limit the amount of returned results
        :type limit: int
        :return: List with cves objects
        :rtype: list
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
