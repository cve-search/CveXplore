from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
)

from sqlalchemy.orm import declarative_base

CveXploreBase = declarative_base()


class Info(CveXploreBase):
    __tablename__ = "info"
    id = Column(Integer, primary_key=True)
    db = Column(String(25))
    lastModified = Column(DateTime)

    def __repr__(self):
        return f"<< Info: {self.db} >>"


class Schema(CveXploreBase):
    __tablename__ = "schema"
    id = Column(Integer, primary_key=True)
    rebuild_needed = Column(Boolean, default=False)
    version = Column(Float)

    def __repr__(self):
        return f"<< Schema: {self.db} >>"
