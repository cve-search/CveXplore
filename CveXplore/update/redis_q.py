import threading
from collections import deque


from queue import Empty, Full, Queue
from time import time

import jsonpickle

from .Config import Configuration
from .db_action import DatabaseAction


class RedisQueue(object):
    def __init__(self, name, serializer=jsonpickle, namespace="queue"):
        self.__db = Configuration.getRedisQConnection()
        self.serializer = serializer
        self._key = "{}:{}".format(name, namespace)

    def __len__(self):
        return self.qsize()

    def __repr__(self):
        return "<< RedisQueue:{} >>".format(self.key)

    def __iter__(self):
        return self

    def __next__(self):
        item = self.get(timeout=1)
        if item is not None:
            if isinstance(item, DatabaseAction):
                item = item.entry
            return item
        else:
            raise StopIteration

    @property
    def key(self):
        return self._key

    def get_full_list(self):

        entries = self.__db.lrange(self.key, 0, -1)

        self.__db.delete(self.key)

        return [self.serializer.decode(entry) for entry in entries]

    def clear(self):
        """Clear the queue of all messages, deleting the Redis key."""
        self.__db.delete(self.key)

    def qsize(self):
        """
        Return size of the queue

        :return:
        :rtype:
        """
        return self.__db.llen(self.key)

    def get(self, block=False, timeout=None):
        """
        Return an item from the queue.

        :param block: Whether or not to wait for item to be available; defaults to False
        :type block: bool
        :param timeout: Time to wait for item to be available in the queue; defaults to None
        :type timeout: int
        :return: Item popped from list
        :rtype: *
        """
        if block:
            if timeout is None:
                timeout = 0
            item = self.__db.blpop(self.key, timeout=timeout)
            if item is not None:
                item = item[1]
        else:
            item = self.__db.lpop(self.key)
        if item is not None and self.serializer is not None:
            item = self.serializer.decode(item)
        return item

    def put(self, *items):
        """
        Put one or more items onto the queue.

        Example:

        q.put("my item")
        q.put("another item")

        To put messages onto the queue in bulk, which can be significantly
        faster if you have a large number of messages:

        q.put("my item", "another item", "third item")
        """
        if self.serializer is not None:
            items = map(self.serializer.encode, items)
        self.__db.rpush(self.key, *items)


# class CveXploreQueue(Queue):
#
#     def __init__(self, name, maxsize=0, serializer=jsonpickle):
#         super().__init__(maxsize)
#         self.name = name
#
#         self.serializer = serializer
#
#     def __repr__(self):
#         return "<< CveXploreQueue:{} >>".format(self.name)
#
#     # Put a new item in the queue
#     def _put(self, item):
#         self.queue.append(self.serializer.encode(item))
#
#         # Get an item from the queue
#     def _get(self):
#         item = self.serializer.decode(self.queue.popleft())
#         if isinstance(item, DatabaseAction):
#             item = item.entry
#         return item
#
#     def getall(self, block=True, timeout=None):
#         with self.not_empty:
#             if self.closed:
#                 raise QueueClosed()
#             if not block:
#                 if not self._qsize():
#                     raise Empty
#             elif timeout is None:
#                 while not self._qsize() and not self.closed:
#                     self.not_empty.wait()
#             elif timeout < 0:
#                 raise ValueError("'timeout' must be a non-negative number")
#             else:
#                 endtime = time() + timeout
#                 while not self._qsize() and not self.closed:
#                     remaining = endtime - time()
#                     if remaining <= 0.0:
#                         raise Empty
#                     self.not_empty.wait(remaining)
#             if self.closed:
#                 raise QueueClosed()
#             items = list(self.queue)
#             items = list(map(self.serializer.decode, items))
#             self.queue.clear()
#             self.not_full.notify()
#             return items
#
#     def iter_queue(self):
#         with self.not_empty:
#             item = self.get(timeout=1)
#             if item is not None:
#                 if isinstance(item, DatabaseAction):
#                     item = item.entry
#                 yield item
#             else:
#                 self.not_full.notify()
#                 raise StopIteration
#
#     def clear(self):
#         with self.not_empty:
#             self.queue.clear()
#             self.not_full.notify()


class QueueClosed(Exception):
    pass


class CveXploreQueue(object):

    def __init__(self, name, maxsize=0, serializer=jsonpickle):
        self.name = name
        self.maxsize = maxsize
        self._init(maxsize)

        self.mutex = threading.Lock()

        self.not_empty = threading.Condition(self.mutex)

        self.not_full = threading.Condition(self.mutex)

        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0
        self.closed = False

        self.serializer = serializer

    def __len__(self):
        self.qsize()

    def __repr__(self):
        return "<< CveXploreQueue:{} >>".format(self.name)

    def __iter__(self):
        return self

    def __next__(self):
        with self.mutex:
            item = self.get(timeout=1)
            if item is not None:
                if isinstance(item, DatabaseAction):
                    item = item.entry
                return item
            else:
                raise StopIteration

    def task_done(self):
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self):
        with self.all_tasks_done:
            while self.unfinished_tasks and not self.closed:
                self.all_tasks_done.wait()

    def qsize(self):
        with self.mutex:
            return self._qsize()

    def empty(self):
        with self.mutex:
            return not self._qsize()

    def full(self):
        with self.mutex:
            return 0 < self.maxsize <= self._qsize()

    def put_nowait(self, item):
        return self.put(item, block=False)

    def get_nowait(self):
        return self.get(block=False)

    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(self.serializer.encode(item))

    def _get(self):
        item = self.serializer.decode(self.queue.popleft())
        if isinstance(item, DatabaseAction):
            item = item.entry
        return item

    def close(self):
        with self.mutex:
            self.closed = True
            self.not_empty.notify_all()
            self.not_full.notify_all()
            self.all_tasks_done.notify_all()

    def getall(self, block=True, timeout=None):
        with self.not_empty:
            if self.closed:
                raise QueueClosed()
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize() and not self.closed:
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize() and not self.closed:
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            if self.closed:
                raise QueueClosed()
            items = list(self.queue)
            items = list(map(self.serializer.decode, items))
            self.queue.clear()
            self.not_full.notify()
            return items

    def iter_queue(self):
        with self.not_empty:
            item = self.get(timeout=1)
            if item is not None:
                if isinstance(item, DatabaseAction):
                    item = item.entry
                yield item
            else:
                self.not_full.notify()
                raise StopIteration

    def clear(self):
        with self.not_empty:
            self.queue.clear()
            self.not_full.notify()

    def put(self, item, block=True, timeout=None):
        with self.not_full:
            if self.closed:
                raise QueueClosed()
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize and not self.closed:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize and not self.closed:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            if self.closed:
                raise QueueClosed()
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self, block=True, timeout=None):
        with self.not_empty:
            if self.closed:
                raise QueueClosed()
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize() and not self.closed:
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize() and not self.closed:
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            if self.closed:
                raise QueueClosed()
            item = self._get()
            self.not_full.notify()
            return item
