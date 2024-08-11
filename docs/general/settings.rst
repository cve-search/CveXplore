Settings
--------

CveXplore by default looks for an .env file in ``${HOME}/.cvexplore`` folder. If certain values need to be
overwritten you can do it either there or pass them directly as environment variables.

On Windows, you would need to set the environment variable ``PYTHONUTF8=1`` for Python.
That will solve many `UnicodeEncodeError`s, e.g., while populating/updating the database.

The following config variables are the configuration settings for CveXplore.
There are more environment variable available for configuring database & backend, documented on their own sections.

General
*******

.. confval:: USER_HOME_DIR

   Directory to use as main directory for storing data, config files and sources initialization files.

.. confval:: CVE_START_YEAR

   The year CVE database population starts from.

.. confval:: CPE_FILTER_DEPRECATED

   Filter out deprecated CPEs.

.. confval:: SOURCES

   Dictionary of external source URLs used for populating the database (in addition to NVD API).

NIST NVD API
************

.. confval:: NVD_NIST_API_KEY

   You can populate CveXplore without an API key, but it will limit the amount of parallel requests made to the NIST API.

   Request an API key from https://nvd.nist.gov/developers/request-an-api-key

.. confval:: NVD_NIST_NO_REJECTED

   Do not import rejected CVEs from the NIST NVD API.

Downloads
*********

.. confval:: MAX_DOWNLOAD_WORKERS

   Maximum count of file download workers.

.. confval:: DOWNLOAD_SEM_FACTOR

    This factor determines the amount of simultaneous requests made towards the NIST API;
    The set amount of client requests (30) get divided with the sem factor, so the lower
    it is set, the more simultaneous requests are made.

    If set, should be set ``>=0.6``.

.. confval:: DOWNLOAD_SLEEP_MIN

   Minimum time randomized sleep between (aiohttp) requests to NVD API.

.. confval::  DOWNLOAD_SLEEP_MAX

   Minimum time randomized sleep between (aiohttp) requests to NVD API.

.. confval:: DOWNLOAD_BATCH_RANGE

   Count of requests made in the time window of ``36`` seconds.

   See https://nvd.nist.gov/general/news/API-Key-Announcement

   Defaults to ``45`` if ``NVD_NIST_API_KEY`` is set, and to ``5`` without.

Proxy
*****

A HTTP proxy can be used for database population & updates.

As CveXplore is using both urllib3 and aiohttp for the connections, the proxy needs to be configured twice in forms supported by each.

.. confval:: HTTP_PROXY_DICT

   Dictionary of proxies used for HTTP & HTTPS connections.

   This is used by urllib3 connections for both NVD API and other sources.

   E.g., ``{ "http": "http://proxy.example.com:8080", "https": "http://proxy.example.com:8080" }``

.. confval:: HTTP_PROXY_STRING

   String presentation of the proxy.
   
   This is used by aiohttp for multiple asynchronous request to NVD API.

   E.g., ``http://proxy.example.com:8080``

Logging
*******

.. confval:: LOGGING_TO_FILE

   Use file logging.

.. confval:: LOGGING_FILE_PATH

   Path for the log directory.

.. confval:: LOGGING_MAX_FILE_SIZE

   Maximum size for a log file.

.. confval:: LOGGING_BACKLOG

   How many files to keep at log rotate.

.. confval:: LOGGING_FILE_NAME

   Filename for log file.

.. confval:: LOGGING_LEVEL

   Short name of the maximum severity level of messages to be logged in log files.

   ``DEBUG > INFO ( > NOTICE > WARNING > ERR > CRIT > ALERT > EMERG )``

.. confval:: SYSLOG_ENABLE

   Use syslog logging.

.. confval:: SYSLOG_SERVER

   IP address of the syslog server.

.. confval:: SYSLOG_PORT

   Port of the syslog server.

.. confval:: SYSLOG_LEVEL

   Short name of the maximum severity level of messages to be logged in syslog.

   ``DEBUG > INFO ( > NOTICE > WARNING > ERR > CRIT > ALERT > EMERG )``

   See https://www.rfc-editor.org/rfc/rfc5424.html#section-6.2.1

.. confval:: GELF_SYSLOG

    GELF format allows for additional fields to be submitted with each log record; Key values of this dict should
    start with underscores; e.g. {"_environment": "SPECIAL"} would append an environment field with the value of
    'SPECIAL' to each log record.

.. confval:: GELF_SYSLOG_ADDITIONAL_FIELDS

   See https://github.com/keeprocking/pygelf?tab=readme-ov-file#static-fields

Redis
*****

.. confval:: REDIS_URL

   Url to be used for contacting redis cache.
