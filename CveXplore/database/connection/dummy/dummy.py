from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase


class DummyConnection(DatabaseConnectionBase):
    def __init__(self, **kwargs):
        super().__init__(logger_name=__name__)

        self._dbclient = {"schema": "test"}

    @property
    def dbclient(self):
        return self._dbclient

    def set_handlers_for_collections(self):
        pass
