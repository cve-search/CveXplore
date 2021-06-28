import datetime
import os
import re
import urllib.parse

import pymongo
import redis

runPath = os.path.dirname(os.path.realpath(__file__))


class Configuration(object):
    CVE_START_YEAR = os.getenv("CVE_START_YEAR", 2002)

    SOURCES = os.getenv(
        "SOURCES",
        {
            "cve": "https://nvd.nist.gov/feeds/json/cve/1.1/",
            "cpe": "https://nvd.nist.gov/feeds/json/cpematch/1.0/nvdcpematch-1.0.json.zip",
            "cwe": "https://cwe.mitre.org/data/xml/cwec_v4.4.xml.zip",
            "capec": "https://capec.mitre.org/data/xml/capec_v3.4.xml",
            "via4": "https://www.cve-search.org/feeds/via4.json",
        },
    )

    HTTP_PROXY = os.getenv("HTTP_PROXY", "")

    LOGGING_MAX_FILE_SIZE = os.getenv("LOGGING_MAX_FILE_SIZE", "100MB")
    LOGGING_BACKLOG = os.getenv("LOGGING_BACKLOG", 5)
    LOGGING_FILE_NAME = os.getenv("LOGGING_FILE_NAME", "./log/update_populate.log")

    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", 27017)
    MONGO_DB = os.getenv("MONGO_DB", "cvexdb")
    MONGO_USER = os.getenv("MONGO_USER", "")
    MONGO_PASS = os.getenv("MONGO_PASS", "")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_PASS = os.getenv("REDIS_PASS", None)
    REDIS_Q = os.getenv("REDIS_Q", 9)

    @classmethod
    def getCVEStartYear(cls):
        next_year = datetime.datetime.now().year + 1
        start_year = cls.CVE_START_YEAR
        if start_year < cls.CVE_START_YEAR or start_year > next_year:
            print(
                "The year %i is not a valid year.\ndefault year %i will be used."
                % (start_year, cls.default["CVEStartYear"])
            )
            start_year = cls.default["CVEStartYear"]
        return start_year

    @classmethod
    def getProxy(cls):
        return cls.HTTP_PROXY

    @classmethod
    def getFeedURL(cls, source):
        return cls.SOURCES[source]

    @classmethod
    def toPath(cls, path):
        return path if os.path.isabs(path) else os.path.join(runPath, "..", path)

    @classmethod
    def getUpdateLogFile(cls):
        return cls.toPath(cls.LOGGING_FILE_NAME)

    @classmethod
    def getMaxLogSize(cls):
        size = cls.LOGGING_MAX_FILE_SIZE
        split = re.findall("\d+|\D+", size)
        multipliers = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}
        if len(split) == 2:
            base = int(split[0])
            unit = split[1].strip().upper()
            return base * multipliers.get(unit, 1024 * 1024)
        # if size is not a correctly defined set it to 100MB
        else:
            return 100 * 1024 * 1024

    @classmethod
    def getBacklog(cls):
        return cls.LOGGING_BACKLOG

    @classmethod
    def getMongoConnection(cls):
        mongoHost = cls.MONGO_HOST
        mongoPort = cls.MONGO_PORT
        mongoDB = cls.MONGO_DB
        mongoUsername = urllib.parse.quote(cls.MONGO_USER)
        mongoPassword = urllib.parse.quote(cls.MONGO_PASS)
        if mongoUsername and mongoPassword:
            mongoURI = "mongodb://{username}:{password}@{host}:{port}/{db}".format(
                username=mongoUsername,
                password=mongoPassword,
                host=mongoHost,
                port=mongoPort,
                db=mongoDB,
            )
        else:
            mongoURI = "mongodb://{host}:{port}/{db}".format(
                host=mongoHost, port=mongoPort, db=mongoDB
            )
        connect = pymongo.MongoClient(mongoURI, connect=False)
        return connect[mongoDB]

    @classmethod
    def getRedisQConnection(cls):
        redisHost = cls.REDIS_HOST
        redisPort = cls.REDIS_PORT
        redisDB = cls.REDIS_Q
        redisPass = cls.REDIS_PASS
        return redis.Redis(
            host=redisHost,
            port=redisPort,
            db=redisDB,
            password=redisPass,
            charset="utf-8",
            decode_responses=True,
        )
