import logging
from abc import ABC, abstractmethod

from CveXplore.core.logging.logger_class import AppLogger

logging.setLoggerClass(AppLogger)


class DatabaseConnectionBase(ABC):
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def __repr__(self):
        return f"<<{self.__class__.__name__}>>"

    @property
    @abstractmethod
    def dbclient(self):
        raise NotImplementedError

    @abstractmethod
    def set_handlers_for_collections(self):
        raise NotImplementedError
