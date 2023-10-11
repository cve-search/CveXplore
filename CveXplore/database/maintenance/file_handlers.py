"""
File Handlers
=============
"""
import shutil
from abc import abstractmethod
from typing import Tuple

from CveXplore.database.maintenance.DownloadHandler import DownloadHandler
from CveXplore.database.maintenance.IJSONHandler import IJSONHandler
from CveXplore.database.maintenance.db_action import DatabaseAction


class JSONFileHandler(DownloadHandler):
    """
    This class handles all JSON related download processing and functions as a base class for specific JSON sources
    processing and downloading
    """

    def __init__(self, feed_type: str, prefix: str):
        super().__init__(feed_type)

        self.is_update = True

        self.prefix = prefix

        self.ijson_handler = IJSONHandler()

    def __repr__(self):
        """return string representation of object"""
        return "<< JSONFileHandler:{} >>".format(self.feed_type)

    def file_to_queue(self, file_tuple: Tuple[str, str]):
        """
        Method responsible for transferring file contents to the worker queue for further processing and inserting them
        into the database
        """

        working_dir, filename = file_tuple

        # adjust the interval counter for debug logging when updating
        if self.is_update:
            interval = 500
        else:
            interval = 5000

        x = 0
        self.logger.debug("Starting processing of file: {}".format(filename))
        for cpe in self.ijson_handler.fetch(filename=filename, prefix=self.prefix):
            self.process_item(item=cpe)
            x += 1
            if x % interval == 0:
                self.logger.debug(
                    "Processed {} entries from file: {}".format(x, filename)
                )

        try:
            self.logger.debug("Removing working dir: {}".format(working_dir))
            shutil.rmtree(working_dir)
        except Exception as err:
            self.logger.error(
                "Failed to remove working dir; error produced: {}".format(err)
            )

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def populate(self, **kwargs):
        raise NotImplementedError


class XMLFileHandler(DownloadHandler):
    """
    This class handles all XML related download processing and functions as a base class for specific XML sources
    processing and downloading
    """

    def __init__(self, feed_type: str):
        super().__init__(feed_type)
        self.is_update = True

    def __repr__(self):
        """return string representation of object"""
        return "<< XMLFileHandler:{} >>".format(self.feed_type)

    def process_item(self, item: dict):
        """
        Method responsible for putting items into the worker queue as database actions
        """

        if self.is_update:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.UpdateOne,
                    collection=self.feed_type.lower(),
                    doc=item,
                )
            )
        else:
            self.queue.put(
                DatabaseAction(
                    action=DatabaseAction.actions.InsertOne,
                    collection=self.feed_type.lower(),
                    doc=item,
                )
            )

    @abstractmethod
    def file_to_queue(self, *args):
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def populate(self, **kwargs):
        raise NotImplementedError
