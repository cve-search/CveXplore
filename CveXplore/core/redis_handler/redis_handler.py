import logging
import uuid
from contextlib import contextmanager

from redis import Redis

from CveXplore.common.config import Configuration


class RedisHandler(object):
    """
    Redis Handler for CveXplore which handlers several Redis related operations.

    Group:
        backend
    """

    def __init__(self, redis_client: Redis):
        """
        Create a new RedisHandler instance

        Args:
            redis_client: A Redis client instance
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = Configuration

        self.redis_client = redis_client

    def _request_lock(self, lock_key: str) -> bool:
        """
        Method to request a lock. A lock is set into Redis and takes the `lock_key` as an argument for it's key.
        Lock is set to the `CELERY_RESULT_EXPIRES` configuration variable.

        Args:
            lock_key: The string to use as the lock key.

        Returns:
            True if lock is acquired, False otherwise
        Group:
            backend
        """
        got_lock = False
        while not got_lock:
            if self.redis_client.get(lock_key) is None:
                self.redis_client.set(
                    lock_key,
                    f"{uuid.uuid4()}",
                    ex=self.config.CELERY_RESULT_EXPIRES,
                )
                got_lock = True
            else:
                got_lock = False

        self.logger.info(f"Lock request: {lock_key} -> Lock request result: {got_lock}")

        return got_lock

    @contextmanager
    def acquire_lock(self, lock_key: str) -> bool:
        """
        Context manager to acquire a lock; lock is deleted when context manager exits.

        Args:
            lock_key:

        Returns:
            True if lock is acquired, False otherwise
        """
        lock_acquired = self._request_lock(lock_key=lock_key)

        try:
            self.logger.info(f"Lock acquired! -> {lock_key}")
            yield lock_acquired
        finally:
            if lock_acquired:
                self.redis_client.delete(lock_key)
                self.logger.info(f"Releasing lock: {lock_key}")
