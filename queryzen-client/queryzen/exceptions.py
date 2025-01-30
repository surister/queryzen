class ZenAlreadyExists(Exception):
    pass


class ZenDoesNotExist(Exception):
    pass


class UnknownError(Exception):
    def __init__(self, message: str):
        self.message = f'Error from api uncaught:  {message}'
        super().__init__(self.message)
