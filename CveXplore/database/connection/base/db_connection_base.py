import logging

from CveXplore.core.logging.logger_class import AppLogger

logging.setLoggerClass(AppLogger)


class DatabaseConnectionBase(object):
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def __repr__(self):
        return f"<<{self.__class__.__name__}>>"
