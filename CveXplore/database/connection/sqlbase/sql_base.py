from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.database.connection.sqlbase.sql_client import SQLClient


class SQLBaseConnection(DatabaseConnectionBase):
    def __init__(self, **kwargs):
        super().__init__(logger_name=__name__)

        self._dbclient = {
            "info": SQLClient("info"),
            "cpe": SQLClient("cpe"),
            "schema": SQLClient("schema"),
        }

    @property
    def dbclient(self):
        return self._dbclient

    def set_handlers_for_collections(self):
        pass
