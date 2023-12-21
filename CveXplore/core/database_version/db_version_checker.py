import json
import os

from CveXplore.core.database_maintenance.update_base_class import UpdateBaseClass
from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.errors import DatabaseSchemaVersionError

runPath = os.path.dirname(os.path.realpath(__file__))


class DatabaseVersionChecker(UpdateBaseClass):
    def __init__(self, datasource: DatabaseConnectionBase):
        super().__init__(logger_name=__name__)

        with open(os.path.join(runPath, "../../.schema_version")) as f:
            self.schema_version = json.loads(f.read())

        database = datasource

        self.dbh = database.dbclient["schema"]

    def validate_schema(self):
        try:
            if (
                not self.schema_version["version"]
                == list(self.dbh.find({}))[0]["version"]
            ):
                if not self.schema_version["rebuild_needed"]:
                    raise DatabaseSchemaVersionError(
                        "Database is not on the latest schema version; please update the database!"
                    )
                else:
                    raise DatabaseSchemaVersionError(
                        "Database schema is not up to date; please re-populate the database!"
                    )
            else:
                return True
        except IndexError:
            # something went wrong fetching the result from the database; assume re-populate is needed
            raise DatabaseSchemaVersionError(
                "Database schema is not up to date; please re-populate the database!"
            )

    def update(self):
        self.logger.info("Updating schema version")

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

        self.logger.info("Update schema version done!")
