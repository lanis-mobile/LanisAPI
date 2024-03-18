class LanisException(Exception):
    pass


class NotSupportedException(LanisException):
    def __init__(self, message):
        super().__init__(message)
