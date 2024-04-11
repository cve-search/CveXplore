import logging
from abc import ABC, abstractmethod

from sqlalchemy import insert

from CveXplore.core.database_models.models import Cpe, Info
from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.database.connection.sqlbase.connection import Session


class SQLClientBase(ABC):
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def __repr__(self):
        return f"<<{self.__class__.__name__}>>"

    @abstractmethod
    def bulk_write(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def insert_many(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def drop(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update_one(self, *args, **kwargs):
        raise NotImplementedError


class SQLClient(SQLClientBase):
    def __init__(self, collection_name: str):
        super().__init__(logger_name=__name__)
        self.session = Session
        self.collection_name = collection_name

        self.model_mapping = {"info": Info, "cpe": Cpe}

    def bulk_write(self, write_entries: list, ordered: bool = False):
        with self.session() as session:
            session.execute(
                insert(self.model_mapping[self.collection_name]), write_entries
            )
            session.commit()

    def insert_many(self, write_entries: list, ordered: bool = False):
        with self.session() as session:
            session.execute(
                insert(self.model_mapping[self.collection_name]), write_entries
            )
            session.commit()

    def delete_one(self, *args, **kwargs):
        pass

    def drop(self, *args, **kwargs):
        pass

    def update_one(self, *args, **kwargs):
        pass


class SQLBaseConnection(DatabaseConnectionBase):
    def __init__(self, **kwargs):
        super().__init__(logger_name=__name__)

        self._dbclient = {
            "info": SQLClient("info"),
            "cpe": SQLClient("cpe"),
            "schema": "test",
        }

    @property
    def dbclient(self):
        return self._dbclient

    def set_handlers_for_collections(self):
        pass
