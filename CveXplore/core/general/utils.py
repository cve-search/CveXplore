import pymongo


def sanitize(x: list | pymongo.cursor.Cursor):
    if isinstance(x, pymongo.cursor.Cursor):
        x = list(x)
    if type(x) == list:
        for y in x:
            sanitize(y)
    if x and "_id" in x:
        x.pop("_id")
    return x
