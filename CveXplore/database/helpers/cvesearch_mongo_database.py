"""
Mongodb specific
================
"""
from pymongo.collection import Collection
from pymongo.cursor import Cursor


class CveSearchCollection(Collection):
    """
    The CveSearchCollection is a custom Collection based on the pymongo Collection class which has been altered to
    return a CveSearchCursor reference on the find method.
    """

    def __init__(self, database, name: str, **kwargs):
        """
        Get / create a custon cve-search Mongo collection.
        """

        super().__init__(database, name, **kwargs)

    def __repr__(self):
        """Return string representation of this class"""
        return f"<< CveSearchCollection:{self.name} >>"

    def find(self, *args, **kwargs):
        """
        Query the database as you would do so with a pymongo Collection.
        """
        return CveSearchCursor(self, *args, **kwargs)


class CveSearchCursor(Cursor):
    """
    The CveSearchCursor is a custom cursor based on the pymongo cursor which will return database objects instead of
    the raw data from the mongodb database.
    """

    def __init__(self, collection: CveSearchCollection, *args, **kwargs):
        """
        Create a new cve-search cursor.
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
        """Return string representation of this class"""
        return f"<< CveSearchCursor:{self.collection} >>"
