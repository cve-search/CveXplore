import collections

supported_datasources = {"MONGODB", "API", "MYSQL"}

datasources = collections.namedtuple("datasources", "MONGODB, API, MYSQL")(
    "mongodb", "api", "mysql"
)
