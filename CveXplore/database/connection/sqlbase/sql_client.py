from sqlalchemy import insert, text
from sqlalchemy.exc import IntegrityError

from CveXplore.database.connection.sqlbase.connection import Session
from CveXplore.database.connection.sqlbase.sql_client_base import SQLClientBase
from CveXplore.database_models.models import (
    Cpe,
    Info,
    Schema,
    Cwe,
    Capec,
    Cves,
    Via4,
    Cpeother,
    MgmtBlacklist,
    MgmtWhitelist,
)


class SQLClient(SQLClientBase):
    def __init__(self, collection_name: str):
        super().__init__(logger_name=__name__)
        self.session = Session
        self.collection_name = collection_name

        self.model_mapping = {
            "info": Info,
            "cpe": Cpe,
            "cves": Cves,
            "schema": Schema,
            "cwe": Cwe,
            "capec": Capec,
            "via4": Via4,
            "cpeother": Cpeother,
            "mgmt_blacklist": MgmtBlacklist,
            "mgmt_whitelist": MgmtWhitelist,
        }

        self.obj_ref = self.model_mapping[self.collection_name]

    def __repr__(self):
        return f"<< SQLClient:{self.collection_name} >>"

    def list_collection_names(self):
        return list(self.model_mapping.keys())

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

    def insert_one(self, record: dict, *args, **kwargs):
        with self.session() as session:
            entry = self.obj_ref(**record)
            session.add(entry)
            session.commit()

    def delete_one(self, query_dict: dict, *args, **kwargs):
        query_key, query_value = list(query_dict.items())[0]

        with self.session() as session:
            session.query(self.obj_ref).filter(
                getattr(self.obj_ref, query_key) == query_value
            ).delete()
            session.commit()

    def drop(self, *args, **kwargs):
        with self.session() as session:
            session.execute(text(f"TRUNCATE TABLE {self.collection_name}"))
            session.commit()

    def update_one(
        self, query_dict: dict, update_dict: dict, upsert: bool = False, *args, **kwargs
    ):
        query_key, query_value = list(query_dict.items())[0]

        with self.session() as session:
            if upsert:
                query_dict.update(update_dict["$set"])
                try:
                    self.insert_one(query_dict)
                except IntegrityError:
                    session.query(self.obj_ref).filter(
                        getattr(self.obj_ref, query_key) == query_value
                    ).update(update_dict["$set"])
                    session.commit()
            else:
                session.query(self.obj_ref).filter(
                    getattr(self.obj_ref, query_key) == query_value
                ).update(update_dict["$set"])
                session.commit()

    def find(self, query_dict: dict, *args, **kwargs):
        with self.session() as session:
            if len(query_dict) == 0:
                data = session.query(self.obj_ref).all()
                return data
            else:
                q = session.query(self.obj_ref)
                for attr, value in query_dict.items():
                    if isinstance(value, dict):
                        for k, v in value.items():
                            if k == "$lte":
                                q = q.filter(
                                    getattr(self.obj_ref, attr) <= value["$lte"]
                                )
                            elif k == "$gte":
                                q = q.filter(
                                    getattr(self.obj_ref, attr) >= value["$gte"]
                                )
                            elif k == "$lt":
                                q = q.filter(getattr(self.obj_ref, attr) < value["$lt"])
                            elif k == "$gt":
                                q = q.filter(getattr(self.obj_ref, attr) > value["$gt"])
                            else:
                                raise ValueError(f"Unsupported key {k} -> {value}")
                    else:
                        q = q.filter(getattr(self.obj_ref, attr) == value)

                data = q.all()

                return data

    def find_one(self, query_dict: dict, *args, **kwargs):
        with self.session() as session:
            if len(query_dict) == 0:
                data = session.query(self.obj_ref).first()
                return data
            else:
                q = session.query(self.obj_ref)
                for attr, value in query_dict.items():
                    if isinstance(value, dict):
                        for k, v in value.items():
                            if k == "$lte":
                                q = q.filter(
                                    getattr(self.obj_ref, attr) <= value["$lte"]
                                )
                            elif k == "$gte":
                                q = q.filter(
                                    getattr(self.obj_ref, attr) >= value["$gte"]
                                )
                            elif k == "$lt":
                                q = q.filter(getattr(self.obj_ref, attr) < value["$lt"])
                            elif k == "$gt":
                                q = q.filter(getattr(self.obj_ref, attr) > value["$gt"])
                            else:
                                raise ValueError(f"Unsupported key {k} -> {value}")
                    else:
                        q = q.filter(getattr(self.obj_ref, attr) == value)

                data = q.first()

                return data
