"""
Cve Search API
==============
"""
import pymongo

from CveXplore.core.api_base_class import ApiBaseClass


class CveSearchApi(ApiBaseClass):
    """
    The CveSearchApi handles the different arguments in order to perform a query to a specific Cve Search api endpoint.
    It mimics the pymongo cursor's behaviour to provide an ambiguous way to talk to either an API or a mongodb.
    """

    def __init__(
        self,
        db_collection,
        filter: dict = None,
        limit: int = None,
        skip: int = None,
        sort: tuple = None,
    ):
        """
        Create a new CveSearchApi object.
        """
        super().__init__(
            address=db_collection.baseurl,
            api_path=db_collection.api_path,
            proxies=db_collection.proxies,
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
        return f"<<CveSearchApi:({self.db_collection.address[0]}, {self.db_collection.address[1]})>>"

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

    def limit(self, value: int):
        """
        Method to limit the amount of returned data
        """

        if not isinstance(value, int):
            raise TypeError("limit must be an integer")

        self.__limit = value

        self.__data["limit"] = self.__limit

        return self

    def skip(self, value: int):
        """
        Method to skip the given amount of records before returning the data
        """

        if not isinstance(value, int):
            raise TypeError("skip must be an integer")

        self.__skip = value

        self.__data["skip"] = self.__skip

        return self

    def sort(self, field: str, direction: int):
        """
        Method to sort the returned data
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
        """Make this class an iterator"""
        self.query()
        return self

    def next(self):
        """Iterate to the results and return database objects"""
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
