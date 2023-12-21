"""
Mongo DB connection
===================
"""
import atexit

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.database.helpers.cvesearch_mongo_database import CveSearchCollection
from CveXplore.errors import DatabaseConnectionException


class MongoDBConnection(DatabaseConnectionBase):
    """
    The MongoDBConnection class serves as a shell that functions as uniform way to connect to the mongodb backend.
    By default, it will try to establish a connection towards a mongodb running on localhost (default port 27017) and
    database 'cvedb' (as per defaults of cve_search)
    """

    def __init__(
        self,
        host: str = "mongodb://127.0.0.1:27017",
        port: int = None,
        database: str = "cvedb",
        **kwargs,
    ):
        """
        The `host` parameter can be a full `mongodb URI <http://dochub.mongodb.org/core/connections>`_, in addition to
        a simple hostname.
        """
        super().__init__(logger_name=__name__)

        self.client = None
        self._dbclient = None

        self.client = MongoClient(host, port, connect=False, **kwargs)

        self._dbclient = self.client[database]

        try:
            collections = self.dbclient.list_collection_names()
        except ServerSelectionTimeoutError as err:
            raise DatabaseConnectionException(
                f"Connection to the database failed: {err}"
            )

        if len(collections) != 0:
            for each in collections:
                self.__setattr__(
                    f"store_{each}",
                    CveSearchCollection(database=self.dbclient, name=each),
                )

        atexit.register(self.disconnect)

    @property
    def dbclient(self):
        return self._dbclient

    def set_handlers_for_collections(self):
        for each in self.dbclient.list_collection_names():
            if not hasattr(self, each):
                setattr(
                    self,
                    f"store_{each}",
                    CveSearchCollection(database=self.dbclient, name=each),
                )

    def disconnect(self):
        """
        Disconnect from mongodb
        """
        if self.client is not None:
            self.client.close()

    def __del__(self):
        """Called when the class is garbage collected."""
        self.disconnect()
