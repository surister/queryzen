# pylint: disable=C0114


class ZenAlreadyExists(Exception):
    """Trying to create a ``Zen`` that already exists."""
    pass


class ZenDoesNotExistError(Exception):
    """Trying to get a ``Zen`` that does not exist.
    """
    pass


class IncompatibleAPIError(Exception):
    """
    Raised when the library is not marked to work against the backend that the queries are being
    sent to.
    """
    # Todo add message
    pass


class ExecutionEngineError(Exception):
    """Workers or the broker is unavailable."""
    pass


class MissingParametersError(Exception):
    """Trying to run a Query without the needed parameters"""
    pass


class DatabaseDoesNotExistError(Exception):
    """Trying to run a zen to a database that does not exist"""
    pass


class UncaughtBackendError(Exception):
    """Backend returns an error code that we do not implicitly catch.
    User is never meant to get this.
    """

    def __init__(self, response: 'QueryZenResponse', zen: 'Zen' = None, context: str = None):
        self.message = f"""
        Error from backend not caught gracefully, this is a bug, please report this entire
        message in a Github Issue:

        https://github.com/surister/queryzen/issues/new?template=Blank+issue

        Response from backend:
        --
        {response!r}

        Involved Zen (if any):
        --
        {zen}

        Extra context:
        --
        {context}
        """
        super().__init__(self.message)
