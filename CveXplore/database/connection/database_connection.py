from CveXplore.api.connection.api_db import ApiDatabaseSource
from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.database.connection.mongodb.mongo_db import MongoDBConnection


class DatabaseConnection(object):
    def __init__(self, database_type: str, database_init_parameters: dict):
        self.database_type = database_type
        self.database_init_parameters = database_init_parameters

        self._database_connnections = {
            "mongodb": MongoDBConnection,
            "api": ApiDatabaseSource,
        }

        self._database_connection = self._database_connnections[self.database_type](
            **self.database_init_parameters
        )

    @property
    def database_connection(self) -> DatabaseConnectionBase:
        return self._database_connection
