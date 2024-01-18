"""
Configuration
=============
"""
import ast
import json
import os
from json import JSONDecodeError


def getenv_bool(name: str, default: str = "False"):
    raw = os.getenv(name, default).title()
    try:
        the_bool = ast.literal_eval(raw)

        if not isinstance(the_bool, bool):
            raise ValueError
    except ValueError:
        raise

    return the_bool


def getenv_list(name: str, default: list = None):
    if default is None:
        default = []

    raw = os.getenv(name, default)

    if not isinstance(raw, list):
        try:
            the_list = json.loads(raw.replace("\n", ""))
            return the_list
        except JSONDecodeError:
            raise

    return default


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

    USER_HOME_DIR = os.path.expanduser("~/.cvexplore")

    CVE_START_YEAR = int(os.getenv("CVE_START_YEAR", 2000))

    CPE_FILTER_DEPRECATED = getenv_bool("CPE_FILTER_DEPRECATED", "True")

    # Which datasource to query.Currently supported options include:
    # - mongodb
    # - api
    DATASOURCE_TYPE = os.getenv("DATASOURCE_TYPE", "mongodb")

    DATASOURCE_PROTOCOL = os.getenv("DATASOURCE_PROTOCOL", "mongodb")
    DATASOURCE_DBAPI = os.getenv("DATASOURCE_DBAPI", None)
    DATASOURCE_HOST = os.getenv(
        "DATASOURCE_HOST", os.getenv("MONGODB_HOST", "127.0.0.1")
    )
    DATASOURCE_PORT = int(
        os.getenv("DATASOURCE_PORT", int(os.getenv("MONGODB_PORT", 27017)))
    )

    DATASOURCE_USER = os.getenv("DATASOURCE_USER", "cvexplore")
    DATASOURCE_PASSWORD = os.getenv("DATASOURCE_PASSWORD", "cvexplore")
    DATASOURCE_DBNAME = os.getenv("DATASOURCE_DBNAME", "cvexplore")

    DATASOURCE_CONNECTION_DETAILS = None

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"{DATASOURCE_PROTOCOL}://{DATASOURCE_USER}:{DATASOURCE_PASSWORD}@{DATASOURCE_HOST}:{DATASOURCE_PORT}/{DATASOURCE_DBNAME}"
        if DATASOURCE_DBAPI is None
        else f"{DATASOURCE_PROTOCOL}+{DATASOURCE_DBAPI}://{DATASOURCE_USER}:{DATASOURCE_PASSWORD}@{DATASOURCE_HOST}:{DATASOURCE_PORT}/{DATASOURCE_DBNAME}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv_bool(
        "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
    )
    SQLALCHEMY_ENGINE_OPTIONS = getenv_dict(
        "SQLALCHEMY_ENGINE_OPTIONS", {"pool_recycle": 299, "pool_timeout": 20}
    )

    # keep these for now to maintain backwards compatibility
    API_CONNECTION_DETAILS = None
    MONGODB_CONNECTION_DETAILS = None
    MONGODB_HOST = os.getenv("MONGODB_HOST", "127.0.0.1")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))

    if os.getenv("SOURCES") is not None:
        SOURCES = getenv_dict("SOURCES", None)
    else:
        with open(os.path.join(USER_HOME_DIR, ".sources.ini")) as f:
            SOURCES = json.loads(f.read())

    NVD_NIST_API_KEY = os.getenv("NVD_NIST_API_KEY", None)
    NVD_NIST_NO_REJECTED = getenv_bool("NVD_NIST_NO_REJECTED", "True")
    HTTP_PROXY_DICT = getenv_dict("HTTP_PROXY_DICT", {})
    HTTP_PROXY_STRING = os.getenv("HTTP_PROXY_STRING", "")

    DEFAULT_SOURCES = {
        "cwe": "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip",
        "capec": "https://capec.mitre.org/data/xml/capec_latest.xml",
        "via4": "https://www.cve-search.org/feeds/via4.json",
        "epss": "https://epss.cyentia.com/epss_scores-current.csv.gz",  # See EPSS at https://www.first.org/epss
    }

    LOGGING_TO_FILE = getenv_bool("LOGGING_TO_FILE", "True")
    LOGGING_FILE_PATH = os.getenv(
        "LOGGING_FILE_PATH", os.path.join(USER_HOME_DIR, "log")
    )

    if not os.path.exists(LOGGING_FILE_PATH):
        os.mkdir(LOGGING_FILE_PATH)

    LOGGING_MAX_FILE_SIZE = (
        int(os.getenv("LOGGING_MAX_FILE_SIZE", 100)) * 1024 * 1024
    )  # in MB
    LOGGING_BACKLOG = int(os.getenv("LOGGING_BACKLOG", 5))
    LOGGING_FILE_NAME = os.getenv("LOGGING_FILE_NAME", "./cvexplore.log")
    LOGGING_UPDATE_FILE_NAME = os.getenv("LOGGING_FILE_NAME", "update_populate.log")
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")

    SYSLOG_ENABLE = getenv_bool("SYSLOG_ENABLE", "False")
    SYSLOG_SERVER = os.getenv("SYSLOG_SERVER", "172.16.1.1")
    SYSLOG_PORT = int(os.getenv("SYSLOG_PORT", 5140))
    SYSLOG_LEVEL = os.getenv("SYSLOG_LEVEL", "DEBUG")

    GELF_SYSLOG = getenv_bool("GELF_SYSLOG", "True")
    # GELF format allows for additional fields to be submitted with each log record; Key values of this dict should
    # start with underscores; e.g. {"_environment": "SPECIAL"} would append an environment field with the value of
    # 'SPECIAL' to each log record.
    GELF_SYSLOG_ADDITIONAL_FIELDS = getenv_dict("GELF_SYSLOG_ADDITIONAL_FIELDS", None)

    MAX_DOWNLOAD_WORKERS = int(os.getenv("MAX_DOWNLOAD_WORKERS", 10))

    # This factor determines the amount of simultaneous requests made towards the NIST API;
    # The set amount of client requests (30) get divided with the sem factor, so the lower
    # it is set, the more simultaneous requests are made.
    DOWNLOAD_SEM_FACTOR = float(
        os.getenv("DOWNLOAD_SEM_FACTOR", 0.0)
    )  # if set, should be set >=0.6
    DOWNLOAD_SLEEP_MIN = float(os.getenv("DOWNLOAD_SLEEP_MIN", 0.5))
    DOWNLOAD_SLEEP_MAX = float(os.getenv("DOWNLOAD_SLEEP_MAX", 2.5))
    DOWNLOAD_BATCH_RANGE = os.getenv("DOWNLOAD_BATCH_RANGE", None)

    def __repr__(self):
        return f"<< CveXploreConfiguration >>"
