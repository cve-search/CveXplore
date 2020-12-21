"""
Specific database functions
===========================
"""
from pymongo import DESCENDING

from CveXplore.database.helpers.generic_db import GenericDatabaseFactory


class CvesDatabaseFunctions(GenericDatabaseFactory):
    """
    The CvesDatabaseFunctions is a specific class that provides the cves attribute of a CveXplore instance additional
    functions that only apply to the 'cves' collection
    """

    def __init__(self, collection):
        super().__init__(collection)

    def get_cves_for_vendor(self, vendor, limit=0):
        """
        Function to return cves based on a given vendor. By default to result is sorted descending on th cvss field.

        :param vendor: A vendor to search for; e.g. microsoft
        :type vendor: str
        :param limit: Limit the amount of returned results
        :type limit: int
        :return: List with cves objects
        :rtype: list
        """

        return list(
            self._datasource_collection_connection.find({"vendors": vendor})
            .limit(limit)
            .sort("cvss", DESCENDING)
        )

    def __repr__(self):
        """ String representation of object """
        return "<< CvesDatabaseFunctions:{} >>".format(self._collection)
