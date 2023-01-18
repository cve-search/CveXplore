from abc import abstractmethod

from CveXplore.api.nvd_nist.nvd_nist_api import NvdNistApi
from CveXplore.database.maintenance.DownloadHandler import DownloadHandler
from CveXplore.database.maintenance.db_action import DatabaseAction


class NVDApiHandler(DownloadHandler):
    """
    This class handles all JSON related download processing and functions as a base class for specific JSON sources
    processing and downloading
    """

    def __init__(self, feed_type):
        super().__init__(feed_type)

        self.is_update = True

        self.api_handler = NvdNistApi()

    def __repr__(self):
        """return string representation of object"""
        return "<< NVDApiHandler:{} >>".format(self.feed_type)

    def process_item(self, item):
        item = self.process_the_item(item)

        if item is not None:
            if self.is_update:
                return DatabaseAction(
                    action=DatabaseAction.actions.UpdateOne,
                    collection=self.feed_type.lower(),
                    doc=item,
                ).entry
            else:
                return DatabaseAction(
                    action=DatabaseAction.actions.InsertOne,
                    collection=self.feed_type.lower(),
                    doc=item,
                ).entry

    @abstractmethod
    def process_the_item(self, *args):
        raise NotImplementedError

    @abstractmethod
    def file_to_queue(self, *args):
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def populate(self, **kwargs):
        raise NotImplementedError
