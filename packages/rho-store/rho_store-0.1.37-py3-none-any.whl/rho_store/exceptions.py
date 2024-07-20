class RhoStoreError(Exception):
    """Base exception"""

    pass


class NotFound(RhoStoreError):
    pass


class RhoApiError(RhoStoreError):
    pass


class RhoServerTimeout(RhoStoreError):
    pass


class InvalidArgument(RhoStoreError):
    pass


class InvalidApiKey(RhoStoreError):
    pass


class FailedToGetData(RhoStoreError):
    pass
