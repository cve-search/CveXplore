"""
API connection
==============
"""
from CveXplore.api.helpers.cve_search_api import CveSearchApi
from CveXplore.common.db_mapping import database_mapping


class ApiDatabaseSource(object):
    """
    The ApiDatabaseSource mimics the behaviour of the MongoDBConnection.
    """

    def __init__(
        self,
        baseurl: str,
        api_path: str = None,
        proxies: dict = None,
        user_agent: str = "CveXplore",
    ):
        """
        Create new instance of the ApiDatabaseSource
        """

        self.database_mapping = database_mapping

        self.baseurl = baseurl

        for each in self.database_mapping:
            setattr(
                self,
                f"store_{each}",
                ApiDatabaseCollection(
                    baseurl=baseurl,
                    api_path=api_path,
                    proxies=proxies,
                    user_agent=user_agent,
                    collname=each,
                ),
            )

    def __repr__(self):
        """return a string representation of the obj ApiDatabaseSource"""
        return f"<< ApiDatabaseSource: {self.baseurl} >>"


class ApiDatabaseCollection(object):
    """
    The ApiDatabaseCollection mimics the behaviour of the CveSearchCollection
    """

    def __init__(
        self,
        baseurl: str,
        collname: str,
        api_path: str = None,
        proxies: dict = None,
        user_agent="CveXplore",
    ):
        """
        Create a new ApiDatabaseCollection.
        """

        self.baseurl = baseurl
        self.api_path = api_path
        self.proxies = proxies
        self.user_agent = user_agent

        self.collname = collname

    def find(self, the_filter: dict = None):
        """
        Query the api endpoint as you would do so with a pymongo Collection.
        """

        return CveSearchApi(self, the_filter)

    def find_one(self, the_filter: dict = None):
        """
        Query the api endpoint as you would do so with a pymongo Collection.

        :return: Data or None
        :rtype: object
        """

        cursor = self.find(the_filter)

        for result in cursor.limit(-1):
            return result
        return None

    def __repr__(self):
        """return a string representation of the obj ApiDatabaseCollection"""
        return f"<< ApiDatabaseCollection: {self.baseurl} >>"
