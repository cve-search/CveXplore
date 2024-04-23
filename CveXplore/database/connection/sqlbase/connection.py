from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from CveXplore.common.config import Configuration

config = Configuration

if config.DATASOURCE_TYPE != "mongodb":
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)

    Session = sessionmaker(bind=engine)
