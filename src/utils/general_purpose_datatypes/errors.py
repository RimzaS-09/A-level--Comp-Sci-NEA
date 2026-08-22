from enum import Enum

class ErrorCodes(Enum):
    pass


class Error (Exception):
    """
    ### Custom Error types for the program
    """
    
    def __init__(self, msg = "Base class error"):
        self.msg = msg

        super().__init__(msg)

    def __str__(self):
        return self.msg
    

class QueueError(Error):
    pass

class QueueFullError(QueueError):
    pass

class QueueEmptyError(QueueError):
    pass


class FileNotFoundError(Error):
    pass