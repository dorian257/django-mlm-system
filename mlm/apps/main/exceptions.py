"""
MLM Client Related Exceptions
"""


class MLMException(Exception):
    pass


class InvalidClientParentError(MLMException):
    pass


class InvalidAffiliationError(MLMException):
    pass


class OperationAmountError(MLMException):
    pass


class OperationClientError(MLMException):
    pass
