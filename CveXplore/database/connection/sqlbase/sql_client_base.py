import logging
from abc import ABC, abstractmethod


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
    def insert_one(self, *args, **kwargs):
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

    @abstractmethod
    def find(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def find_one(self, *args, **kwargs):
        raise NotImplementedError
