"""
Data source connection
======================
"""
import json
import os

from CveXplore.database.connection.database_connection import DatabaseConnection
from CveXplore.objects.cvexplore_object import CveXploreObject


class DatasourceConnection(CveXploreObject):
    """
    The DatasourceConnection class handles the connection to the data source and is the base class for the database
    objects and generic database functions
    """

    def __init__(self, collection: str):
        """
        Create a DatasourceConnection object
        """
        super().__init__()
        self._collection = collection

    @property
    def datasource_connection(self):
        # hack for documentation building
        if json.loads(os.getenv("DOC_BUILD"))["DOC_BUILD"] == "YES":
            return DatabaseConnection(
                database_type="dummy",
                database_init_parameters={},
            ).database_connection
        else:
            return DatabaseConnection(
                database_type=self.config.DATASOURCE_TYPE,
                database_init_parameters=self.config.DATASOURCE_CONNECTION_DETAILS,
            ).database_connection

    @property
    def datasource_collection_connection(self):
        return getattr(self.datasource_connection, f"store_{self.collection}")

    @property
    def collection(self):
        return self._collection

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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__
