"""
Mongo DB connection
===================
"""
import atexit

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from CveXplore.database.helpers.cvesearch_mongo_database import CveSearchCollection
from CveXplore.errors import DatabaseEmptyException, DatabaseConnectionException


class MongoDBConnection(object):
    """
    The MongoDBConnection class serves as a shell that functions as uniform way to connect to the mongodb backend.
    By default it will try to establish a connection towards a mongodb running on localhost (default port 27017) and
    database 'cvedb' (as per defaults of cve_search)
    """

    def __init__(
        self, host="mongodb://127.0.0.1:27017", port=None, database="cvedb", **kwargs
    ):

        self.client = None
        self.__dbclient = None

        if host == "dummy":
            from mongoengine import connect
            self.client = connect('mydb')
        else:
            self.client = MongoClient(host, port, connect=False, **kwargs)

        self.__dbclient = self.client[database]

        try:
            collections = self.__dbclient.list_collection_names()
        except ServerSelectionTimeoutError as err:
            raise DatabaseConnectionException(
                "Connection to the database failed: {}".format(err)
            )

        if len(collections) != 0:
            for each in collections:
                self.__setattr__(
                    "store_{}".format(each),
                    CveSearchCollection(database=self.__dbclient, name=each),
                )
        else:
            raise DatabaseEmptyException(
                "No collection found in the database named: {}".format(
                    self.__dbclient.name
                )
            )

        atexit.register(self.disconnect)

    @property
    def get_collections_details(self):

        for each in self.__dbclient.list_collections():
            yield each

    @property
    def get_collection_names(self):

        return self.__dbclient.list_collection_names()

    def disconnect(self):
        """
        Disconnect from mongodb
        """
        if self.client is not None:
            self.client.close()

    def __del__(self):
        """Called when the class is garbage collected."""
        self.disconnect()

    def __repr__(self):
        """ String representation of object """
        return "<< MongoDBConnection:{} >>".format(self.__dbclient.name)
