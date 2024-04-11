from sqlalchemy import insert

from CveXplore.core.database_models.models import Cpe, Info
from CveXplore.database.connection.sqlbase.connection import Session
from CveXplore.database.connection.sqlbase.sql_client_base import SQLClientBase


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
