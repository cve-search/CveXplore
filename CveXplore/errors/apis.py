class ApiException(Exception):
    pass


class ApiErrorException(ApiException):
    pass


class ApiDataError(ApiException):
    pass


class ApiDataRetrievalFailed(ApiException):
    pass


class ApiMaxRetryError(ApiException):
    pass
