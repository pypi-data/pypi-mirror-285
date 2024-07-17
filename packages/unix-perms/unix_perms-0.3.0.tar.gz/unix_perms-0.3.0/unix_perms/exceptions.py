class BaseError(Exception):
    """Base error class."""
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class InvalidOctalError(BaseError):
    """Error that represents an invalid octal entered by user."""
    def __init__(self, message: str):
        super().__init__(message=message)
