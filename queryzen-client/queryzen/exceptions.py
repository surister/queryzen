class ZenAlreadyExists(Exception):
    pass


class ZenDoesNotExist(Exception):
    pass


class UnknownError(Exception):
    # TODO (ivan), rename UnknownError to UncaughtBackendError. Make it beautifully print
    # the response in the console so if it ever happens, we get a faster Q/A + bugfix.

    # Ideally, we receive one 'context', string where we the developer explain the context
    # from which this was thrown, e.g. UnknownError("When creating a Zen, the JSON representation of the object was not returned", ...)
    # Structure of the raised error:

    Exception(
        """
        Error from backend not caught gracefully, this is a bug, please report this entire message in a Github Issue.
        https://github.com/t/asdfhasdfs <- link to create issue template.
        
        Response from backend:
        
        Response(
            status_code = 200,
            error_message = "error message",    
        )
        
        Involved Zen (if Any)
        
        Zen(
            name='zen',
            ...
        )
        
        """

    )
    def __init__(self, message: str, status_code: int):
        self.message = f'Error from backend not caught gracefully, this is a bug, please report it: {status_code} {message}'
        super().__init__(self.message)
