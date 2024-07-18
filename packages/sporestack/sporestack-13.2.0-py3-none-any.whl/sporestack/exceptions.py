class SporeStackError(Exception):
    pass


class SporeStackUserError(SporeStackError):
    """HTTP 4XX"""

    pass


class SporeStackTooManyRequestsError(SporeStackError):
    """HTTP 429, retry again later"""

    pass


class SporeStackPaymentRequiredError(SporeStackError):
    """HTTP 402, token needs more funds to complete the action."""

    pass


class SporeStackServerError(SporeStackError):
    """HTTP 5XX"""

    pass
