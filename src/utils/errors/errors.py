from enum import Enum

class Error (Exception):
    """
    ### Custom Error types for the program
    
    A new error type will be created by simply inheriting this base error type. only __init__ and err_type will be overridden, so that the message can be changed.
    """
    
    # This'll be just the class type for the sub
    err_type = "Base class error"
    
    
    def __init__(self, msg = "Base class error"):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return self.err_type + ": " + self.msg