import collections

from pymongo import InsertOne, UpdateOne


class DatabaseAction(object):
    """
    Database Action class is used to queue update and insert actions.

    Group:
        database
    """

    actions = collections.namedtuple("Actions", "InsertOne UpdateOne")(0, 1)

    def __init__(self, action: actions, doc: dict, upsert: bool = True):
        """
        Create a DatabaseAction object.

        Args:
            action: Action to use
            doc: Entry to perform action with
        """
        self.action = action
        self.doc = doc
        self.upsert = upsert

    @property
    def entry(self):
        """
        Show the entry property for this class

        Returns:
            The entry property for this class.
        Group:
            properties
        """
        if self.action == self.actions.InsertOne:
            return InsertOne(self.doc)
        elif self.action == self.actions.UpdateOne:
            return UpdateOne(
                {"id": self.doc["id"]}, {"$set": self.doc}, upsert=self.upsert
            )
