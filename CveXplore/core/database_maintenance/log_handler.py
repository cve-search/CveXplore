"""
Log Handler
===========
"""
import logging
import platform
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

import colors

from CveXplore.common.config import Configuration


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

    config = Configuration()

    logDict = {
        "version": 1,
        "disable_existing_loggers": False,
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
        "loggers": {
            "CveXplore": {
                "handlers": ["consoleHandler"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

    dictConfig(logDict)

    level_map = {
        "debug": "magenta",
        "info": "white",
        "warning": "yellow",
        "error": "red",
        "critical": "red",
    }

    def __init__(self, name: str, level: int | str = logging.NOTSET):
        super().__init__(name, level)

    def debug(self, msg: str, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘DEBUG’ and color *MAGENTA*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

            >>> logger.debug('Houston, we have a thorny problem')

        """

        msg = colors.color(f"{msg}", fg=HelperLogger.level_map["debug"])

        return super(HelperLogger, self).debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘INFO’ and color *WHITE*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

            >>> logger.info('Houston, we have an interesting problem')

        """

        msg = colors.color(f"{msg}", fg=HelperLogger.level_map["info"])

        return super(HelperLogger, self).info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘WARNING’ and color *YELLOW*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

            >>> logger.warning('Houston, we have a bit of a problem')

        """

        msg = colors.color(f"{msg}", fg=HelperLogger.level_map["warning"])

        return super(HelperLogger, self).warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘ERROR’ and color *RED*.

        Store logged message to the database for dashboard alerting.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

            >>> logger.error('Houston, we have a major problem')

        """

        msg = colors.color(f"{msg}", fg=HelperLogger.level_map["error"])

        return super(HelperLogger, self).error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘CRITICAL’ and color *RED*.

        Store logged message to the database for dashboard alerting.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

            >>> logger.critical('Houston, we have a hell of a problem')

        """

        msg = colors.color(f"{msg}", fg=HelperLogger.level_map["critical"])

        return super(HelperLogger, self).critical(msg, *args, **kwargs)


class UpdateHandler(HelperLogger):
    """
    The UpdateHandler is used by the update process to provide written and visual feedback to the initiator of database
    management tasks.
    """

    def __init__(self, name: str, level: int | str = logging.NOTSET):
        super().__init__(name, level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        if self.config.LOGGING_TO_FILE:
            crf = RotatingFileHandler(
                filename=self.config.getUpdateLogFile(),
                maxBytes=self.config.getMaxLogSize(),
                backupCount=self.config.getBacklog(),
            )
            crf.setLevel(logging.DEBUG)
            crf.setFormatter(formatter)
            self.addHandler(crf)
