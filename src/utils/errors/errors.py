from enum import Enum

class Error (Exception):
    """
    ### Custom Error types for the program
    
    A new error type will be created by simply inheriting this base error type. Only `err_type` and 'err_msg' will be overridden,
    so that the message can be changed.
    """
    
    # This'll be just the class type for the sub
    err_type = "Base class error"
    
    err_msg = "Base class for errors"
    
    def __init__(self, msg = None):
        if msg is None:
            msg  = self.err_msg
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return self.err_type + ": " + self.msg
    

class IntRangeError(Error):
    err_type = "Integer out of range error"
    err_msg = "Integer is out of acceptable range of values"


class LocationNotFoundError(Error):
    err_type = "Location Error"
    err_msg = "A location couldn't be found on the map"

class RouteNotFoundError(Error):
    err_type = "No route found Error"
    err_msg = "No connected route could be found for the locations"
    


class StackFullError(Error):
    err_type = "Stack full Error"
    err_msg = "The static stack has reached it's size limit"

class StackEmptyError(Error):
    err_type = "Stack Empty Error"
    err_msg = "The stack is empty and cannot be popped any further"


class QueueFullError(Error):
    err_type = "Queue full Error"
    err_msg = "The static Queue has reached it's size limit"

class QueueEmptyError(Error):
    err_type = "Queue Empty Error"
    err_msg = "The Queue is empty and cannot be dequeued any further"