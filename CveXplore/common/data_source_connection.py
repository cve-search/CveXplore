import json
import os

from pymongo.collection import Collection

from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.database.connection.database_connection import DatabaseConnection
from CveXplore.objects.cvexplore_object import CveXploreObject


class DatasourceConnection(CveXploreObject):
    """
    The DatasourceConnection class handles the connection to the data source and is the base class for the database
    objects and generic database functions

    Group:
        common
    """

    def __init__(self, collection: str):
        """
        Create a DatasourceConnection object

        Args:
            collection: The name of the data source collection

        """
        super().__init__()
        self._collection = collection

    @property
    def datasource_connection(self) -> DatabaseConnectionBase:
        """
        Property to access the datasource connection

        Group:
            properties

        """
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
    def datasource_collection_connection(self) -> Collection:
        """
        Property to access the datasource collection connection

        Group:
            properties

        """
        return getattr(self.datasource_connection, f"store_{self.collection}")

    @property
    def collection(self) -> str:
        """
        Property to access the collection

        Group:
            properties

        """
        return self._collection

    def to_dict(self, *print_keys: str) -> dict:
        """
        Method to convert the entire object to a dictionary

        Args:
            print_keys: Keys to limit the output dictionary

        Returns:
            A dictionary of the requested keys

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

    def __eq__(self, other: DatabaseConnection) -> bool:
        return self.__dict__ == other.__dict__

    def __ne__(self, other: DatabaseConnection) -> bool:
        return self.__dict__ != other.__dict__
