"""
Data source connection
======================
"""
import json
import os

from CveXplore.api.connection.api_db import ApiDatabaseSource
from CveXplore.database.connection.mongo_db import MongoDBConnection


class DatasourceConnection(object):
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

    def __init__(self, collection):
        """
        Create a DatasourceConnection object

        :param collection: Define the collection to connect to
        :type collection: str
        """
        self.__collection = collection

    @property
    def _datasource_connection(self):
        return DatasourceConnection.__DATA_SOURCE_CONNECTION

    @property
    def _datasource_collection_connection(self):
        return getattr(
            DatasourceConnection.__DATA_SOURCE_CONNECTION,
            "store_{}".format(self.__collection),
        )

    @property
    def _collection(self):
        return self.__collection
