import calendar
from datetime import datetime

import colors
import pymongo

from CveXplore.database_models.models import CveXploreModel


def sanitize(x: list | pymongo.cursor.Cursor):
    if isinstance(x, pymongo.cursor.Cursor):
        x = list(x)
    if type(x) == list:
        for y in x:
            sanitize(y)
    if isinstance(x, CveXploreModel):
        x = x.to_dict()
    if x and "_id" in x:
        x.pop("_id")
    return x


def timestamp_to_datetime(timestamp):
    """
    Method that will take the provided timestamp and converts it into a date time object

    :param timestamp: unix timestamp
    :type timestamp: int
    :return: date time object
    :rtype: datetime
    """
    value = datetime.utcfromtimestamp(timestamp)

    return value


def datetime_to_timestamp(date_time_object):
    return calendar.timegm(date_time_object.utctimetuple())


def datetime_to_timestring(datetime_object):
    return timestamp_to_datetimestring(datetime_to_timestamp(datetime_object))


def timestamp_to_datetimestring(timestamp, vis=False):
    """
    Method that will take the provided timestamp and converts it into a RFC3339 date time string

    :param timestamp: unix timestamp
    :type timestamp: int
    :return: date time object
    :rtype: datetime.datetime (format: '%d-%m-%YT%H:%M:%SZ')
    """
    value = datetime.utcfromtimestamp(timestamp)

    if not vis:
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        return value.strftime("%Y-%m-%d %H:%M:%S")


def set_ansi_color_red(msg: str) -> str:
    return colors.color("{}".format(msg), fg="red")


def set_ansi_color_green(msg: str) -> str:
    return colors.color("{}".format(msg), fg="green")


def set_ansi_color_magenta(msg: str) -> str:
    return colors.color("{}".format(msg), fg="magenta")


def set_ansi_color_yellow(msg: str) -> str:
    return colors.color("{}".format(msg), fg="yellow")
