from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase


class SQLBase(DatabaseConnectionBase):
    def __init__(self):
        super().__init__(logger_name=__name__)

        self._dbclient = None

    @property
    def dbclient(self):
        return self._dbclient
