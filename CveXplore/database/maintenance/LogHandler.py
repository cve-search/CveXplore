"""
Log Handler
===========
"""
import logging
import os
import platform
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

import colors

from .Config import Configuration


class HostnameFilter(logging.Filter):
    hostname = platform.node()

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True


class HelperLogger(logging.Logger):
    """
    The HelperLogger is used by the application / gui as their logging class and *extends* the default python
    logger.logging class.
    """

    runPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    logPath = os.path.join(runPath, "log")

    if not os.path.exists(logPath):
        os.makedirs(logPath)

    config = Configuration()

    logDict = {
        "version": 1,
        "formatters": {
            "sysLogFormatter": {
                "format": "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
            },
            "simpleFormatter": {
                "format": "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
            },
        },
        "handlers": {
            "consoleHandler": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "stream": "ext://sys.stdout",
                "formatter": "simpleFormatter",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["consoleHandler"]},
    }

    dictConfig(logDict)

    level_map = {
        "debug": "magenta",
        "info": "white",
        "warning": "yellow",
        "error": "red",
        "critical": "red",
    }

    def __init__(self, name, level=logging.NOTSET):

        super().__init__(name, level)

    def debug(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘DEBUG’ and color *MAGENTA.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        .. code-block:: python

            >>> logger.debug(“Houston, we have a thorny problem”)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=HelperLogger.level_map["debug"])

        return super(HelperLogger, self).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘INFO’ and color *WHITE*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        .. code-block:: python

            >>> logger.info(“Houston, we have an interesting problem”)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=HelperLogger.level_map["info"])

        return super(HelperLogger, self).info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘WARNING’ and color *YELLOW*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        .. code-block:: python

            >>> logger.warning(“Houston, we have a bit of a problem”)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=HelperLogger.level_map["warning"])

        return super(HelperLogger, self).warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘ERROR’ and color *RED*.

        Store logged message to the database for dashboard alerting.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        .. code-block:: python

            >>> logger.error(“Houston, we have a major problem”)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=HelperLogger.level_map["error"])

        return super(HelperLogger, self).error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘CRITICAL’ and color *RED*.

        Store logged message to the database for dashboard alerting.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        .. code-block:: python

            >>> logger.critical(“Houston, we have a hell of a problem”)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=HelperLogger.level_map["critical"])

        return super(HelperLogger, self).critical(msg, *args, **kwargs)


class UpdateHandler(HelperLogger):
    """
    The UpdateHandler is used by the update process to provide written and visual feedback to the initiator of database
    management tasks.
    """

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        crf = RotatingFileHandler(
            filename=self.config.getUpdateLogFile(),
            maxBytes=self.config.getMaxLogSize(),
            backupCount=self.config.getBacklog(),
        )
        crf.setLevel(logging.DEBUG)
        crf.setFormatter(formatter)
        self.addHandler(crf)
