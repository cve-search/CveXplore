"""
Configuration
=============
"""
import ast
import json
import os
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

    USER_HOME_DIR = user_wd

    CVE_START_YEAR = int(os.getenv("CVE_START_YEAR", 2000))

    CPE_FILTER_DEPRECATED = getenv_bool("CPE_FILTER_DEPRECATED", "True")

    # Which datasource to query.Currently supported options include:
    # - mongodb
    # - api
    DATASOURCE = os.getenv("DATASOURCE", "mongodb")

    DATASOURCE_PROTOCOL = os.getenv("DATASOURCE_PROTOCOL", "mongodb")
    DATASOURCE_HOST = os.getenv(
        "DATASOURCE_HOST", os.getenv("MONGODB_HOST", "127.0.0.1")
    )
    DATASOURCE_PORT = int(
        os.getenv("DATASOURCE_PORT", int(os.getenv("MONGODB_PORT", 27017)))
    )

    # keep these for now to maintain backwards compatibility
    MONGODB_HOST = os.getenv("MONGODB_HOST", "127.0.0.1")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))

    if os.getenv("SOURCES") is not None:
        SOURCES = getenv_dict("SOURCES", None)
    else:
        with open(os.path.join(user_wd, ".sources.ini")) as f:
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
    LOGGING_FILE_PATH = os.getenv("LOGGING_FILE_PATH", os.path.join(user_wd, "log"))

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
