"""
Mongodb specific
================
"""
from pymongo.collection import Collection
from pymongo.cursor import Cursor


class CveSearchCursor(Cursor):
    """
    The CveSearchCursor is a custom cursor based on the pymongo cursor which will return database objects instead of
    the raw data from the mongodb database.
    """

    def __init__(self, collection, *args, **kwargs):
        """
        Create a new cve-search cursor.

        :param collection: Reference to a CveSearchCollection object
        :type collection: CveSearchCollection
        """
        super().__init__(collection, *args, **kwargs)

        from CveXplore.objects.capec import Capec
        from CveXplore.objects.cpe import Cpe
        from CveXplore.objects.cves import Cves
        from CveXplore.objects.cwe import Cwe
        from CveXplore.objects.via4 import Via4

        self.database_objects_mapping = {
            "capec": Capec,
            "cpe": Cpe,
            "cwe": Cwe,
            "via4": Via4,
            "cves": Cves,
        }

    @property
    def __empty(self):
        return self._Cursor__empty

    @property
    def __data(self):
        return self._Cursor__data

    @property
    def __manipulate(self):
        return self._Cursor__manipulate

    @property
    def __collection(self):
        return self._Cursor__collection

    @property
    def __collname(self):
        return self._Cursor__collname

    def next(self):
        """
        Advance the cursor and return CveXplore objects
        """
        if self.__empty:
            raise StopIteration
        if len(self.__data) or self._refresh():
            if self.__manipulate:
                _db = self.__collection.database
                try:
                    return _db._fix_outgoing(
                        self.database_objects_mapping[self.__collname](
                            **self.__data.popleft()
                        ),
                        self.__collection,
                    )
                except KeyError:
                    return _db._fix_outgoing(self.__data.popleft(), self.__collection)
            else:
                try:
                    return self.database_objects_mapping[self.__collname](
                        **self.__data.popleft()
                    )
                except KeyError:
                    return self.__data.popleft()
        else:
            raise StopIteration

    __next__ = next

    def __repr__(self):
        """ Return string representation of this class """
        return "<< CveSearchCursor:{} >>".format(self.collection)


class CveSearchCollection(Collection):
    """
    The CveSearchCollection is a custom Collection based on the pymongo Collection class which has been altered to
    return a CveSearchCursor reference on the find method.
    """

    def __init__(self, database, name, **kwargs):
        """
        Get / create a custon cve-search Mongo collection.

        :param database: the database to get a collection from
        :type database: MongoDBConnection
        :param name: the name of the collection to get
        :type name: str
        :param kwargs: additional keyword arguments will be passed as options for the create collection command
        :type kwargs: kwargs
        """

        super().__init__(database, name, **kwargs)

    def __repr__(self):
        """ Return string representation of this class """
        return "<< CveSearchCollection:{} >>".format(self.name)

    def find(self, *args, **kwargs):
        """
        Query the database as you would do so with a pymongo Collection.

        :return: Reference to the CveSearchCursor
        :rtype: CveSearchCursor
        """
        return CveSearchCursor(self, *args, **kwargs)
