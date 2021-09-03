"""
CPE Converters
==============
"""
from urllib.parse import unquote


def from2to3CPE(cpe, autofill=False):
    """
    Method to transform cpe2.2 to cpe2.3 format

    :param cpe: cpe2.2 string
    :type cpe: str
    :param autofill: Whether to cpe string should be autofilled with double quotes and hyphens
    :type autofill: bool
    :return: cpe2.3 formatted string
    :rtype: str
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:2.3:"):
        if not cpe.startswith("cpe:/"):
            # can not do anything with this; returning original string
            return cpe
        cpe = cpe.replace("cpe:/", "cpe:2.3:")
        cpe = cpe.replace("::", ":-:")
        cpe = cpe.replace("~-", "~")
        cpe = cpe.replace("~", ":-:")
        cpe = cpe.replace("::", ":")
        cpe = cpe.strip(":-")
        cpe = unquote(cpe)
    if autofill:
        e = cpe.split(":")
        for x in range(0, 13 - len(e)):
            cpe += ":*"
    return cpe


def from3to2CPE(cpe):
    """
    Method to transform cpe2.3 to cpe2.2 format

    :param cpe: cpe2.3 string
    :type cpe: str
    :return: cpe2.2 string
    :rtype: str
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:/"):
        if not cpe.startswith("cpe:2.3:"):
            # can not do anything with this; returning original string
            return cpe
        cpe = cpe.replace("cpe:2.3:", "")
        parts = cpe.split(":")
        next = []
        first = "cpe:/" + ":".join(parts[:5])
        last = parts[5:]
        if last:
            for x in last:
                next.append("~") if x == "-" else next.append(x)
            if "~" in next:
                pad(next, 6, "~")
        cpe = "%s:%s" % (first, "".join(next))
        cpe = cpe.replace(":-:", "::")
        cpe = cpe.strip(":")
    return cpe


def pad(seq, target_length, padding=None):
    length = len(seq)
    if length > target_length:
        return seq
    seq.extend([padding] * (target_length - length))
    return seq
