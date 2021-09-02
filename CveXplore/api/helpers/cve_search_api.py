"""
Cve Search API
==============
"""
import pymongo

from CveXplore.common.generic_api import GenericApi


class CveSearchApi(GenericApi):
    """
    The CveSearchApi handles the different arguments in order to perform a query to a specific Cve Search api endpoint.
    It mimics the pymongo cursor's behaviour to provide an ambiguous way to talk to either an API or a mongodb.
    """

    def __init__(self, db_collection, filter=None, limit=None, skip=None, sort=None):
        """
        Create a new CveSearchApi object.

        :param db_collection: ApiDatabaseCollection object
        :type db_collection: ApiDatabaseCollection
        :param filter: Filter to be used when querying data
        :type filter: dict
        :param limit: Limit value
        :type limit: int
        :param skip: Skip value
        :type skip: int
        :param sort: Sort value
        :type sort: tuple
        """
        super().__init__(
            address=tuple(db_collection.address),
            api_path=db_collection.api_path,
            proxies=db_collection.proxies,
            protocol=db_collection.protocol,
            user_agent=db_collection.user_agent,
        )
        from CveXplore.common.db_obj_mapping import database_objects_mapping

        self.database_objects_mapping = database_objects_mapping

        self.db_collection = db_collection

        self.collname = db_collection.collname

        data = filter
        if data is None:
            data = {}

        self.__data = {"retrieve": self.collname, "dict_filter": data}

        self.__empty = False

        self.__limit = limit
        self.__skip = skip
        self.__sort = sort

        self.data_queue = None

    def __repr__(self):
        """return a string representation of the obj GenericApi"""
        return "<<CveSearchApi:({}, {})>>".format(
            self.db_collection.address[0], self.db_collection.address[1]
        )

    def query(self):
        """
        Endpoint for free query to cve search data
        """

        results = self.call(method="POST", resource="query", data=self.__data)

        if isinstance(results, str):
            self.data_queue = None
            return

        try:
            if len(results["data"]) > 0:
                self.data_queue = results["data"]
        except Exception:
            self.data_queue = results

    def limit(self, value):
        """
        Method to limit the amount of returned data

        :param value: Limit
        :type value: int
        :return: CveSearchApi object
        :rtype: CveSearchApi
        """

        if not isinstance(value, int):
            raise TypeError("limit must be an integer")

        self.__limit = value

        self.__data["limit"] = self.__limit

        return self

    def skip(self, value):
        """
        Method to skip the given amount of records before returning the data

        :param value: Skip
        :type value: int
        :return: CveSearchApi object
        :rtype: CveSearchApi
        """

        if not isinstance(value, int):
            raise TypeError("skip must be an integer")

        self.__skip = value

        self.__data["skip"] = self.__skip

        return self

    def sort(self, field, direction):
        """
        Method to sort the returned data

        :param field: Field to sort on
        :type field: str
        :param direction: The direction to sort in; e.g. pymongo.DESCENDING
        :type direction: int
        :return: CveSearchApi object
        :rtype: CveSearchApi
        """

        if direction == pymongo.DESCENDING:
            direction = "DESC"
        else:
            direction = "ASC"

        self.__sort = (field, direction)

        self.__data["sort"] = self.__sort[0]
        self.__data["sort_dir"] = self.__sort[1]

        return self

    def __iter__(self):
        """ Make this class an iterator """
        self.query()
        return self

    def next(self):
        """ Iterate to the results and return database objects """
        if self.__empty:
            raise StopIteration
        if self.data_queue is None:
            raise StopIteration
        try:
            if len(self.data_queue):
                return self.database_objects_mapping[self.collname](
                    **self.data_queue.pop()
                )
            else:
                raise StopIteration
        except TypeError:
            # We've received a Response object
            raise StopIteration

    __next__ = next
