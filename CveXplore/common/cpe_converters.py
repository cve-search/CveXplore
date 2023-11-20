"""
CPE Converters
==============
"""
import re

from CveXplore.database.helpers.cpe_conversion import cpe_uri_to_fs, cpe_fs_to_uri


def from2to3CPE(cpe: str, autofill: bool = False) -> str:
    """
    Method to transform cpe2.2 to cpe2.3 format
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:2.3:"):
        if not cpe.startswith("cpe:/"):
            return False
        cpe = cpe_uri_to_fs(cpe)
    if autofill:
        e = cpe.split(":")
        for x in range(0, 13 - len(e)):
            cpe += ":-"
    return cpe


def from3to2CPE(cpe: str) -> str:
    """
    Method to transform cpe2.3 to cpe2.2 format
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:/"):
        if not cpe.startswith("cpe:2.3:"):
            return False
        cpe = cpe_fs_to_uri(cpe)
    return cpe


def create_cpe_regex_string(str_input: str) -> str:
    # format to cpe2.3
    cpe_string = from2to3CPE(str_input)

    if cpe_string.startswith("cpe"):
        # strict search with term starting with cpe; e.g: cpe:2.3:o:microsoft:windows_7:*:sp1:*:*:*:*:*:*

        remove_trailing_regex_stars = r"(?:\:|\:\:|\:\*)+$"

        cpe_regex = re.escape(re.sub(remove_trailing_regex_stars, "", cpe_string))

        cpe_regex_string = r"^{}:".format(cpe_regex)
    else:
        # more general search on same field; e.g. microsoft:windows_7
        cpe_regex_string = f"{re.escape(cpe_string)}"

    return cpe_regex_string
