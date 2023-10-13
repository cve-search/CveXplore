"""
Generic database functions
==========================
"""
import re

from CveXplore.common.data_source_connection import DatasourceConnection
from CveXplore.common.db_mapping import database_mapping


class GenericDatabaseFactory(DatasourceConnection):
    """
    The GenericDatabaseFactory handles the creation of general, collection based, functions which provide an instance
    of CveXplore functions that apply to the given collection.
    """

    def __init__(self, collection: str):
        """
        Create a new GenericDatabaseFactory and create field specific functions based on the __default_fields and
        the __fields_mapping.
        """
        super().__init__(collection=collection)

        self.__database_mapping = database_mapping

        self.__default_fields = ["id"]

        self.__fields_mapping = {
            "capec": [
                "name",
                "summary",
                "prerequisites",
                "solutions",
                "loa",
                "typical_severity",
            ],
            "cpe": ["title", "cpeName", "vendor", "product"],
            "cwe": ["name", "status", "Description"],
            "cves": [
                "cvss",
                "cvss3",
                "summary",
                "vendors",
                "products",
                "lastModified",
                "modified",
                "published",
                "status",
                "assigner",
                "cwe",
            ],
        }

        total_fields_list = (
            self.__default_fields + self.__fields_mapping[self._collection]
        )
        for field in total_fields_list:
            setattr(
                self,
                field,
                GenericDatabaseFieldsFunctions(
                    field=field, collection=self._collection
                ),
            )

    def get_by_id(self, doc_id: str):
        """
        Method to fetch a specific collection entry via it's id number
        """

        if not isinstance(doc_id, str):
            try:
                doc_id = str(doc_id)
            except ValueError:
                return "Provided value is not a string nor can it be cast to one"

        return self._datasource_collection_connection.find_one({"id": doc_id})

    def __repr__(self):
        """String representation of object"""
        return "<< GenericDatabaseFactory:{} >>".format(self._collection)


class GenericDatabaseFieldsFunctions(DatasourceConnection):
    """
    The GenericDatabaseFieldsFunctions handles the creation of general, field based, functions
    """

    def __init__(self, field: str, collection: str):
        """
        Create a new GenericDatabaseFieldsFunctions and create field specific functions.
        """
        super().__init__(collection=collection)

        self.__field = field

    def search(self, value: str):
        """
        Method for searching for a given value. The value shall be converted to a regex.
        """

        regex = re.compile(value, re.IGNORECASE)

        query = {self.__field: {"$regex": regex}}

        return self._datasource_collection_connection.find(query)

    def find(self, value: str | dict = None):
        """
        Method to find a given value.
        """

        if value is not None:
            query = {self.__field: value}
        else:
            query = None

        return self._datasource_collection_connection.find(query)

    def __repr__(self):
        """String representation of object"""
        return "<< GenericDatabaseFieldsFunctions:{} >>".format(self._collection)
