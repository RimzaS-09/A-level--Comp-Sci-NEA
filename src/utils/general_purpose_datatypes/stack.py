from utils.errors.errors import StackEmptyError, StackFullError, IntRangeError

class Stack:
    def __init__(self) -> None:
        self._data = []
        self._ptr = -1

    def pop(self):
        raise NotImplementedError
    
    def push(self, item):
        raise NotImplementedError
    
    def peek(self):
        if self._ptr == -1:
            raise StackEmptyError("Stack can't be peeked - No items are in it")
        
        return self._data[self._ptr]

    def is_empty(self) -> bool:
        if self._ptr == -1:
            return True
        return False
    
    def size(self) -> int:
        return self._ptr + 1

class StaticStack(Stack):
    def __init__(self, max_len: int) -> None:
        super().__init__()
        
        if max_len < 1:
            raise IntRangeError("Size of static stack must be a positive non-zero integer.")
        
        self._data = [None] * max_len
    
    def push(self, item):
        if self._ptr == len(self._data) - 1:
            raise StackFullError(f"The static stack has reached its size limit of {len(self._data)} items")
        self._ptr += 1
        
        self._data[self._ptr] =  item

    def pop(self):
        if self._ptr == -1:
            raise StackEmptyError()
        
        return_val = self._data[self._ptr]
        self._ptr -= 1
        return return_val
    
    def max_size(self) -> int:
        return len(self._data)
        
    

class DynamicStack(Stack):
    def __init__(self) -> None:
        super().__init__()
    
    def push(self, item):
        self._ptr += 1
        self._data.append(item)
    
    def pop(self):
        if self._ptr == -1:
            raise StackEmptyError()
        
        return_val = self._data[self._ptr]
        del self._data[self._ptr]
        self._ptr -= 1
        
        return return_val