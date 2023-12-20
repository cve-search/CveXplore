class DatabaseException(Exception):
    pass


class DatabaseEmptyException(DatabaseException):
    pass


class DatabaseConnectionException(DatabaseException):
    pass


class DatabaseIllegalCollection(DatabaseException):
    pass


class UpdateSourceNotFound(DatabaseException):
    pass


class DatabaseSchemaVersionError(DatabaseException):
    pass
