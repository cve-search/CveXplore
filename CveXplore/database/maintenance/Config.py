"""
Configuration
=============
"""
import datetime
import json
import os
import re

runPath = os.path.dirname(os.path.realpath(__file__))


class Configuration(object):
    """
    Class holding the configuration
    """

    CVE_START_YEAR = os.getenv("CVE_START_YEAR", 2002)

    if os.getenv("SOURCES") is not None:
        SOURCES = json.loads(os.getenv("SOURCES"))
    else:
        with open(os.path.join(runPath, "../../.sources.ini")) as f:
            SOURCES = json.loads(f.read())

    DEFAULT_SOURCES = {
        "cve": "https://nvd.nist.gov/feeds/json/cve/1.1/",
        "cpe": "https://nvd.nist.gov/feeds/json/cpematch/1.0/nvdcpematch-1.0.json.zip",
        "cwe": "https://cwe.mitre.org/data/xml/cwec_v4.4.xml.zip",
        "capec": "https://capec.mitre.org/data/xml/capec_v3.5.xml",
        "via4": "https://www.cve-search.org/feeds/via4.json",
    }

    HTTP_PROXY = os.getenv("HTTP_PROXY", "")

    LOGGING_MAX_FILE_SIZE = os.getenv("LOGGING_MAX_FILE_SIZE", "100MB")
    LOGGING_BACKLOG = os.getenv("LOGGING_BACKLOG", 5)
    LOGGING_FILE_NAME = os.getenv("LOGGING_FILE_NAME", "./update_populate.log")

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
        return path if os.path.isabs(path) else os.path.join(runPath, "../..", path)

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
