# pylint: disable=C0114

from queryzen.backend import QueryZenResponse


class ZenAlreadyExists(Exception):
    """
    Raised if you try to create a ``Zen`` that already exists.
    """
    pass


class ZenDoesNotExistError(Exception):
    """
    Raised if you try to get a ``Zen`` that does not exist.
    """
    pass


class IncompatibleAPI(Exception):
    """
    Raised when the library is nor marked to work against the backend that the queries are being
    sent to.
    """
    # Todo add message
    pass


class UncaughtBackendError(Exception):
    """
    Raised when the backend returns an error code that we do not implicitly catch.
    """

    def __init__(self, response: QueryZenResponse, zen: 'Zen' = None, context: str = None):
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
