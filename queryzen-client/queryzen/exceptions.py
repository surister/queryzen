# pylint: disable=C0114


class ZenAlreadyExistsError(Exception):
    """Trying to create a ``Zen`` that already exists."""


class ZenDoesNotExistError(Exception):
    """Trying to get a ``Zen`` that does not exist."""


class IncompatibleAPIError(Exception):
    """
    Raised when the library is not marked to work against the backend that the queries are being
    sent to.
    """
    # Todo add message


class ExecutionEngineError(Exception):
    """Workers or the broker is unavailable."""


class MissingParametersError(Exception):
    """Trying to run a Query without the needed parameters"""


class ParametersMissmatchError(Exception):
    """Trying to pass parameters to a query that does not have them"""


class DatabaseDoesNotExistError(Exception):
    """Trying to run a zen to a database that does not exist"""


class DefaultValueDoesNotExistError(ValueError):
    """Trying to create a default value with two values """


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
