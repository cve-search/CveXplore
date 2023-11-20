"""
Data source connection
======================
"""
import json
import os

from CveXplore.api.connection.api_db import ApiDatabaseSource
from CveXplore.database.connection.mongo_db import MongoDBConnection
from CveXplore.objects.cvexplore_object import CveXploreObject


class DatasourceConnection(CveXploreObject):
    """
    The DatasourceConnection class handles the connection to the data source and is the base class for the database
    objects and generic database functions
    """

    # hack for documentation building
    if json.loads(os.getenv("DOC_BUILD"))["DOC_BUILD"] != "YES":
        __DATA_SOURCE_CONNECTION = (
            ApiDatabaseSource(**json.loads(os.getenv("API_CON_DETAILS")))
            if os.getenv("API_CON_DETAILS")
            else MongoDBConnection(**json.loads(os.getenv("MONGODB_CON_DETAILS")))
        )

    def to_dict(self, *print_keys: str) -> dict:
        """
        Method to convert the entire object to a dictionary
        """

        if len(print_keys) != 0:
            full_dict = {
                k: v
                for (k, v) in self.__dict__.items()
                if not k.startswith("_") and k in print_keys
            }
        else:
            full_dict = {
                k: v for (k, v) in self.__dict__.items() if not k.startswith("_")
            }

        return full_dict

    def __init__(self, collection: str):
        """
        Create a DatasourceConnection object
        """
        super().__init__()
        self.__collection = collection

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    @property
    def _datasource_connection(self):
        return DatasourceConnection.__DATA_SOURCE_CONNECTION

    @property
    def _datasource_collection_connection(self):
        return getattr(
            DatasourceConnection.__DATA_SOURCE_CONNECTION,
            f"store_{self.__collection}",
        )

    @property
    def _collection(self):
        return self.__collection
