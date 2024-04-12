from CveXplore.core.database_models.models import CveXploreBase
from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.database.connection.sqlbase.sql_client import SQLClient
from CveXplore.errors import DatabaseConnectionException


class SQLBaseConnection(DatabaseConnectionBase):
    def __init__(self, **kwargs):
        super().__init__(logger_name=__name__)

        self._dbclient = {
            "info": SQLClient("info"),
            "cpe": SQLClient("cpe"),
            "cves": SQLClient("cves"),
            "schema": SQLClient("schema"),
            "cwe": SQLClient("cwe"),
            "capec": SQLClient("capec"),
            "via4": SQLClient("via4"),
        }

        try:
            collections = list(CveXploreBase.metadata.tables.keys())
        except ConnectionError as err:
            raise DatabaseConnectionException(
                f"Connection to the database failed: {err}"
            )

        if len(collections) != 0:
            for each in collections:
                self.__setattr__(f"store_{each}", SQLClient(each))

    @property
    def dbclient(self):
        return self._dbclient

    def set_handlers_for_collections(self):
        for each in list(CveXploreBase.metadata.tables.keys()):
            if not hasattr(self, each):
                setattr(self, f"store_{each}", SQLClient(each))
