from utils.errors import errors

class Stack:
    def __init__(self) -> None:
        self._data = []
    
    def pop(self):
        return
    
    def push(self, item):
        pass
    
    def peek(self):
        return


class StaticStack(Stack):
    def __init__(self, max_len: int) -> None:
        super().__init__()
        self._data = [None] * max_len
        self._ptr = -1
        
    def pop(self):
        if self._ptr == -1:
            # TODO: StackEmptyError here
            return None
        
        return_val = self._data[self._ptr]
        self._ptr -= 1
        
        return return_val
    
    def push(self, item):
        if self._ptr
    

class DynamicStack(Stack):
    def __init__(self) -> None:
        super().__init__()