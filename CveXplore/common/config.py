"""
Configuration
=============
"""
import ast
import datetime
import json
import os
import re
import shutil
from json import JSONDecodeError

from dotenv import load_dotenv

if not os.path.exists(os.path.expanduser("~/.cvexplore")):
    os.mkdir(os.path.expanduser("~/.cvexplore"))

user_wd = os.path.expanduser("~/.cvexplore")

if not os.path.exists(os.path.join(user_wd, ".env")):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), ".env_example"),
        os.path.join(user_wd, ".env"),
    )

load_dotenv(os.path.join(user_wd, ".env"))

if not os.path.exists(os.path.join(user_wd, ".sources.ini")):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), ".sources.ini"),
        os.path.join(user_wd, ".sources.ini"),
    )


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    return ast.literal_eval(raw)


def getenv_dict(name: str, default: dict = None):
    if default is None:
        default = {}

    raw = os.getenv(name, default)

    if not isinstance(raw, dict):
        try:
            the_dict = json.loads(raw)
            return the_dict
        except JSONDecodeError:
            raise

    return default


class Configuration(object):
    """
    Class holding the configuration
    """

    USER_HOME_DIR = user_wd

    CVE_START_YEAR = os.getenv("CVE_START_YEAR", 2002)

    if os.getenv("SOURCES") is not None:
        SOURCES = getenv_dict("SOURCES", None)
    else:
        with open(os.path.join(user_wd, ".sources.ini")) as f:
            SOURCES = json.loads(f.read())

    NVD_NIST_API_KEY = os.getenv("NVD_NIST_API_KEY", None)
    NVD_NIST_NO_REJECTED = getenv_bool("NVD_NIST_NO_REJECTED", "True")

    DEFAULT_SOURCES = {
        "cwe": "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip",
        "capec": "https://capec.mitre.org/data/xml/capec_latest.xml",
        "via4": "https://www.cve-search.org/feeds/via4.json",
    }

    HTTP_PROXY = os.getenv("HTTP_PROXY", "")

    LOGGING_TO_FILE = getenv_bool("LOGGING_TO_FILE", "True")
    LOGGING_FILE_PATH = os.getenv("LOGGING_FILE_PATH", os.path.join(user_wd, "log"))

    if not os.path.exists(LOGGING_FILE_PATH):
        os.mkdir(LOGGING_FILE_PATH)

    LOGGING_MAX_FILE_SIZE = os.getenv("LOGGING_MAX_FILE_SIZE", "100MB")
    LOGGING_BACKLOG = os.getenv("LOGGING_BACKLOG", 5)
    LOGGING_FILE_NAME = os.getenv("LOGGING_FILE_NAME", "./cvexplore.log")
    LOGGING_UPDATE_FILE_NAME = os.getenv("LOGGING_FILE_NAME", "./update_populate.log")

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
    def getUpdateLogFile(cls):
        return os.path.join(cls.LOGGING_FILE_PATH, cls.LOGGING_UPDATE_FILE_NAME)

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
