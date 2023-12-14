import collections

from pymongo import InsertOne, UpdateOne


class DatabaseAction(object):
    actions = collections.namedtuple("Actions", "InsertOne UpdateOne")(0, 1)

    def __init__(self, action: actions, doc: dict):
        self.action = action
        self.doc = doc

    @property
    def entry(self):
        if self.action == self.actions.InsertOne:
            return InsertOne(self.doc)
        elif self.action == self.actions.UpdateOne:
            return UpdateOne({"id": self.doc["id"]}, {"$set": self.doc}, upsert=True)
