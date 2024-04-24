from queue import Empty, Queue

from CveXplore.common.config import Configuration
from CveXplore.core.database_maintenance.db_action import DatabaseAction
from CveXplore.core.general.datasources import datasources


class WorkerQueue(Queue):
    def __init__(self, name: str, maxsize: int = 0):
        super().__init__(maxsize)
        self.config = Configuration
        self.name = name
        self.maxsize = maxsize

        self.closed = False

    def __len__(self):
        self.qsize()

    def __repr__(self):
        return f"<< WorkerQueue:{self.name} >>"

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.get(timeout=1)
            if item is not None:
                if isinstance(item, DatabaseAction):
                    if self.config.DATASOURCE_TYPE.lower() == datasources.MONGODB:
                        item = item.entry
                    else:
                        item = item.doc
                return item
            else:
                raise StopIteration
        except Empty:
            raise StopIteration

    def getall(self):
        return list(iter(self))

    def clear(self):
        with self.not_empty:
            self.queue.clear()
            self.not_full.notify()
