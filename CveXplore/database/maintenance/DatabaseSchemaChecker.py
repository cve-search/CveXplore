import json
import logging
import os

from CveXplore.database.connection.mongo_db import MongoDBConnection

runPath = os.path.dirname(os.path.realpath(__file__))


class SchemaChecker(object):
    def __init__(self):
        with open(os.path.join(runPath, "../../.schema_version")) as f:
            self.schema_version = json.loads(f.read())

        database = MongoDBConnection(**json.loads(os.getenv("MONGODB_CON_DETAILS")))

        self.dbh = database._dbclient["schema"]

        self.logger = logging.getLogger("SchemaChecker")

    def create_indexes(self):
        # hack for db_updater.py to put this class in the posts variable and run the update method
        self.logger.info("Updating schema version")
        self.update()
        self.logger.info("Update schema version done!")

    def update(self):
        try:

            current_record = list(self.dbh.find({}))

            if len(current_record) != 0:
                current_record[0]["version"] = self.schema_version["version"]
                current_record[0]["rebuild_needed"] = self.schema_version[
                    "rebuild_needed"
                ]

                self.dbh.update_one(
                    {"_id": current_record[0]["_id"]}, {"$set": current_record[0]}
                )
            else:
                current_record = {
                    "version": self.schema_version["version"],
                    "rebuild_needed": self.schema_version["rebuild_needed"],
                }

                self.dbh.insert_one(current_record)
        except AttributeError:
            current_record = {
                "version": self.schema_version["version"],
                "rebuild_needed": self.schema_version["rebuild_needed"],
            }
            self.dbh.insert_one(current_record)
