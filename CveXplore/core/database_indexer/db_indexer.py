from collections import namedtuple

from pymongo import TEXT, ASCENDING

from CveXplore.core.database_maintenance.update_base_class import UpdateBaseClass
from CveXplore.core.general.utils import sanitize
from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase

MongoUniqueIndex = namedtuple("MongoUniqueIndex", "index name unique")
MongoAddIndex = namedtuple("MongoAddIndex", "index name")


class DatabaseIndexer(UpdateBaseClass):
    """
    Class processing the Mongodb indexes
    """

    def __init__(self, datasource: DatabaseConnectionBase):
        super().__init__(logger_name=__name__)

        database = datasource
        self.database = database.dbclient

        self.indexes = {
            "cpe": [
                MongoUniqueIndex(index=[("id", ASCENDING)], name="id", unique=True),
                MongoAddIndex(index=[("vendor", ASCENDING)], name="vendor"),
                MongoAddIndex(index=[("product", ASCENDING)], name="product"),
                MongoAddIndex(index=[("deprecated", ASCENDING)], name="deprecated"),
                MongoAddIndex(index=[("cpeName", ASCENDING)], name="cpeName"),
                MongoAddIndex(index=[("title", ASCENDING)], name="title"),
                MongoAddIndex(index=[("stem", ASCENDING)], name="stem"),
                MongoAddIndex(
                    index=[("padded_version", ASCENDING)], name="padded_version"
                ),
                MongoAddIndex(index=[("lastModified", ASCENDING)], name="lastModified"),
            ],
            "cpeother": [
                MongoUniqueIndex(index=[("id", ASCENDING)], name="id", unique=True)
            ],
            "cves": [
                MongoAddIndex(index=[("id", ASCENDING)], name="id"),
                MongoAddIndex(
                    index=[("vulnerable_configuration", ASCENDING)],
                    name="vulnerable_configuration",
                ),
                MongoAddIndex(
                    index=[("vulnerable_product", ASCENDING)], name="vulnerable_product"
                ),
                MongoAddIndex(index=[("modified", ASCENDING)], name="modified"),
                MongoAddIndex(index=[("published", ASCENDING)], name="published"),
                MongoAddIndex(index=[("lastModified", ASCENDING)], name="lastModified"),
                MongoAddIndex(index=[("cvss", ASCENDING)], name="cvss"),
                MongoAddIndex(index=[("cvss3", ASCENDING)], name="cvss3"),
                MongoAddIndex(index=[("summary", TEXT)], name="summary"),
                MongoAddIndex(index=[("vendors", ASCENDING)], name="vendors"),
                MongoAddIndex(index=[("products", ASCENDING)], name="products"),
                MongoAddIndex(index=[("assigner", ASCENDING)], name="assigner"),
                MongoAddIndex(index=[("cwe", ASCENDING)], name="cwe"),
                MongoAddIndex(index=[("status", ASCENDING)], name="status"),
                MongoAddIndex(
                    index=[("vulnerable_product_stems", ASCENDING)],
                    name="vulnerable_product_stems",
                ),
                MongoAddIndex(
                    index=[("vulnerable_configuration_stems", ASCENDING)],
                    name="vulnerable_configuration_stems",
                ),
                MongoAddIndex(index=[("epss", ASCENDING)], name="epss"),
            ],
            "via4": [MongoAddIndex(index=[("id", ASCENDING)], name="id")],
            "mgmt_whitelist": [MongoAddIndex(index=[("id", ASCENDING)], name="id")],
            "mgmt_blacklist": [MongoAddIndex(index=[("id", ASCENDING)], name="id")],
            "capec": [
                MongoAddIndex(index=[("id", ASCENDING)], name="id"),
                MongoAddIndex(index=[("loa", ASCENDING)], name="loa"),
                MongoAddIndex(
                    index=[("typical_severity", ASCENDING)], name="typical_severity"
                ),
                MongoAddIndex(index=[("name", ASCENDING)], name="name"),
                MongoAddIndex(
                    index=[("related_weakness", ASCENDING)], name="related_weakness"
                ),
            ],
            "cwe": [
                MongoAddIndex(index=[("id", ASCENDING)], name="id"),
                MongoAddIndex(index=[("name", ASCENDING)], name="name"),
                MongoAddIndex(index=[("status", ASCENDING)], name="status"),
            ],
        }

    def getInfo(self, collection: str):
        return sanitize(self.database["info"].find_one({"db": collection}))

    def create_indexes(self, collection: str = None):
        if collection is not None:
            try:
                for each in self.indexes[collection]:
                    if isinstance(each, MongoUniqueIndex):
                        self.setIndex(
                            collection, each.index, name=each.name, unique=each.unique
                        )
                    elif isinstance(each, MongoAddIndex):
                        self.setIndex(collection, each.index, name=each.name)
            except KeyError:
                # no specific index given, continue
                self.logger.warning(
                    f"Could not find the requested collection: {collection}, skipping..."
                )
                pass

        else:
            for index in self.iter_indexes():
                self.setIndex(index[0], index[1])

            for collection in self.indexes.keys():
                for each in self.indexes[collection]:
                    if isinstance(each, MongoUniqueIndex):
                        self.setIndex(
                            collection, each.index, name=each.name, unique=each.unique
                        )
                    elif isinstance(each, MongoAddIndex):
                        self.setIndex(collection, each.index, name=each.name)

    def iter_indexes(self):
        for each in self.get_via4_indexes():
            yield each

    def get_via4_indexes(self):
        via4 = self.getInfo("via4")
        result = []
        if via4:
            for index in via4.get("searchables", []):
                result.append(("via4", index))
        return result

    def setIndex(self, col: str, field: str, **kwargs):
        try:
            self.database[col].create_index(field, **kwargs)
            self.logger.info("Success to create index %s on %s" % (field, col))
        except Exception as e:
            self.logger.error("Failed to create index %s on %s: %s" % (col, field, e))
