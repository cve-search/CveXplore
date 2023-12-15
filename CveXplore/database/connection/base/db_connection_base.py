import logging
from CveXplore.core.logging.logger_class import AppLogger

logging.setLoggerClass(AppLogger)


class DatabaseConnectionBase(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        return f"<<{self.__class__.__name__}>>"
