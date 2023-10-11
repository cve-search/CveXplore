import re
from typing import IO

import dateutil.parser
import pymongo
from dateutil import tz

from CveXplore.database.helpers import cpe_conversion


def sanitize(x: list | pymongo.cursor.Cursor):
    if isinstance(x, pymongo.cursor.Cursor):
        x = list(x)
    if type(x) == list:
        for y in x:
            sanitize(y)
    if x and "_id" in x:
        x.pop("_id")
    return x


def currentTime(utc: bytes | str | IO[str] | IO):
    timezone = tz.tzlocal()
    utc = dateutil.parser.parse(utc)
    output = utc.astimezone(timezone)
    output = output.strftime("%d-%m-%Y - %H:%M")
    return output


def isURL(string: str):
    urlTypes = [re.escape(x) for x in ["http://", "https://", "www."]]
    return re.match("^(" + "|".join(urlTypes) + ")", string)


def vFeedName(string: str):
    string = string.replace("map_", "")
    string = string.replace("cve_", "")
    return string.title()


def mergeSearchResults(database: dict, plugins: dict):
    if "errors" in database:
        results = {"data": [], "errors": database["errors"]}
    else:
        results = {"data": []}

    data = []
    data.extend(database["data"])
    data.extend(plugins["data"])
    for cve in data:
        if not any(cve["id"] == entry["id"] for entry in results["data"]):
            results["data"].append(cve)
    return results


def tk_compile(regexes: str | list | tuple):
    if type(regexes) not in [list, tuple]:
        regexes = [regexes]
    r = []
    for rule in regexes:
        r.append(re.compile(rule))
    return r


# Convert cpe2.2 url encoded to cpe2.3 char escaped
# cpe:2.3:o:cisco:ios:12.2%281%29 to cpe:2.3:o:cisco:ios:12.2\(1\)
def unquote(cpe: str):
    return cpe_conversion.unquote(cpe)


# Generates a human readable title from a CPE 2.3 string
def generate_title(cpe: str):
    title = ""

    cpe_split = cpe.split(":")
    # Do a very basic test to see if the CPE is valid
    if len(cpe_split) == 13:

        # Combine vendor, product and version
        title = " ".join(cpe_split[3:6])

        # If "other" is specified, add it to the title
        if cpe_split[12] != "*":
            title += cpe_split[12]

        # Capitilize each word
        title = title.title()

        # If the target_sw is defined, add "for <target_sw>" to title
        if cpe_split[10] != "*":
            title += " for " + cpe_split[10]

        # In CPE 2.3 spaces are replaced with underscores. Undo it
        title = title.replace("_", " ")

        # Special characters are escaped with \. Undo it
        title = title.replace("\\", "")

    return title
