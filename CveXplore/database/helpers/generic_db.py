"""
Generic database functions
==========================
"""
import re
from functools import reduce
from typing import Union, Iterable

from CveXplore.common.data_source_connection import DatasourceConnection
from CveXplore.common.db_mapping import database_mapping
from CveXplore.objects.cvexplore_object import CveXploreObject


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
            "cpe": ["title", "cpeName", "vendor", "product", "stem"],
            "cwe": ["name", "status", "description"],
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
                "epss",
            ],
        }

        total_fields_list = (
            self.__default_fields + self.__fields_mapping[self.collection]
        )
        for field in total_fields_list:
            setattr(
                self,
                field,
                GenericDatabaseFieldsFunctions(field=field, collection=self.collection),
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

        return self.datasource_collection_connection.find_one({"id": doc_id})

    def mget_by_id(self, *doc_ids: str) -> Union[Iterable[CveXploreObject], Iterable]:
        """
        Method to fetch a specific collection entry via it's id number
        """
        ret_data = []
        for doc_id in doc_ids:
            data = self.get_by_id(doc_id=doc_id)
            if data is not None:
                ret_data.append(data)

        if len(ret_data) >= 1:
            return sorted(ret_data, key=lambda x: x.id)
        else:
            return ret_data

    def _field_list(self, doc_id: str) -> list:
        """
        Method to fetch all field names from a specific collection
        """
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

    def field_list(self, *doc_ids: str) -> list:
        """
        Method to fetch all field names from a specific collection
        """
        ret_data = []
        for doc_id in sorted(doc_ids):
            data = self._field_list(doc_id=doc_id)
            ret_data.append({doc_id: data, "field_count": len(data)})

        return ret_data

    def mapped_fields(self, collection: str) -> list:
        ret_list = []
        try:
            ret_list.extend(self.__fields_mapping[collection])
        except KeyError:
            pass

        ret_list.extend(self.__default_fields)
        return sorted(ret_list)

    def __repr__(self):
        """String representation of object"""
        return f"<< {self.__class__.__name__}:{self.collection} >>"


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

        return self.datasource_collection_connection.find(query)

    def find(self, value: str | dict = None):
        """
        Method to find a given value.
        """

        if value is not None:
            query = {self.__field: value}
        else:
            query = None

        return self.datasource_collection_connection.find(query)

    def __repr__(self):
        """String representation of object"""
        return f"<< GenericDatabaseFieldsFunctions:{self.collection} >>"
