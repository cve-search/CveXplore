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
        address,
        api_path=None,
        proxies=None,
        protocol="https",
        user_agent="CveXplore",
    ):
        """
        Create new instance of the ApiDatabaseSource

        :param address: Tuple with host ip/name and port
        :type address: tuple
        :param api_path: The api_path parameter needs to be provided if the API runs on a non-root path.
                         So if the API is reachable at: https://localhost/api, this parameter needs to be set to 'api'.
                         So it is needed to connect to api resources, defaults to 'None'
        :type api_path: str
        :param proxies: If you need to use a proxy, you can configure individual requests with the proxies argument
                        to any request method
        :type proxies: dict
        :param protocol: Protocol to use when connecting to api; defaults to 'https'
        :type protocol: str
        :param user_agent: User agent to use when connecting; defaults to CveXplore:<<version>>
        :type user_agent: str
        """

        self.database_mapping = database_mapping

        if address == {}:
            return

        self.address = address

        if api_path is not None:
            self.url = "{}://{}:{}/{}".format(
                protocol, address[0], address[1], api_path
            )
        else:
            self.url = "{}://{}:{}".format(protocol, address[0], address[1])

        for each in self.database_mapping:
            setattr(
                self,
                "store_{}".format(each),
                ApiDatabaseCollection(
                    address=address,
                    api_path=api_path,
                    proxies=proxies,
                    protocol=protocol,
                    user_agent=user_agent,
                    collname=each,
                ),
            )

    def __repr__(self):
        """return a string representation of the obj ApiDatabaseSource"""
        return "<< ApiDatabaseSource: {} >>".format(self.address)


class ApiDatabaseCollection(object):
    """
    The ApiDatabaseCollection mimics the behaviour of the CveSearchCollection
    """

    def __init__(
        self,
        address,
        collname,
        api_path=None,
        proxies=None,
        protocol="https",
        user_agent="CveXplore",
    ):
        """
        Create a new ApiDatabaseCollection.

        :param address: Tuple with host ip/name and port
        :type address: tuple
        :param collname: Collection name
        :type collname: str
        :param api_path: The api_path parameter needs to be provided if the API runs on a non-root path.
                         So if the API is reachable at: https://localhost/api, this parameter needs to be set to 'api'.
                         So it is needed to connect to api resources, defaults to 'None'
        :type api_path: str
        :param proxies: If you need to use a proxy, you can configure individual requests with the proxies argument
                        to any request method
        :type proxies: dict
        :param protocol: Protocol to use when connecting to api; defaults to 'https'
        :type protocol: str
        :param user_agent: User agent to use when connecting; defaults to CveXplore:<<version>>
        :type user_agent: str
        """

        self.address = address
        self.api_path = api_path
        self.proxies = proxies
        self.protocol = protocol
        self.user_agent = user_agent

        self.collname = collname

    def find(self, filter=None):
        """
        Query the api endpoint as you would do so with a pymongo Collection.

        :return: Reference to the CveSearchApi
        :rtype: CveSearchApi
        """

        return CveSearchApi(self, filter)

    def find_one(self, filter=None):
        """
        Query the api endpoint as you would do so with a pymongo Collection.

        :return: Data or None
        :rtype: object
        """

        cursor = self.find(filter)

        for result in cursor.limit(-1):
            return result
        return None

    def __repr__(self):
        """return a string representation of the obj ApiDatabaseCollection"""
        return "<< ApiDatabaseCollection: {} >>".format(self.address)
