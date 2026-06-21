"""
This module contains the classes and other relevant tools related to my custom queue data structures
"""

import errors


class QueueValue:
    
    """
    ### A wrapper for the elements within a queue
    Has two sets of data:
    * the actual data in the queue
    * its priority, stored as an int. The lower the int, the higher the priority

    Although circular queues _can_ be used without this wrapping, it allows us to cast between a circular and priority queue more efficiently
    """
    
    
    def __init__(self, data, priority_level: int):
        self.__data = data
        
        # Priority level will be stored as an int
        self.__lvl = int(priority_level)
    
    ### Getters and setters ###
    def get_level(self):
        return self.__lvl
    
    def get_data(self):
        return self.__data



class QueueInterface:
    """
    This is an interface to act as an abstraction of the queue classes. May be used to implement in other queue types, e.g. linear queues
    """
    
    def __init__(self, length: int) -> None:
        pass

    def enqueue(self, element: QueueValue) -> bool:
        pass

    def dequeue(self):
        pass

    def display(self) -> None:
        pass


class DynamicPriorityQueue(QueueInterface):
    def __init__(self):
        # data will be stored as a dynamic array
        self.__data = []   
    
    # Data must be in the format of the class QueueValue
    # An insertion sort pass is performed for every element added
    def enqueue(self, element: QueueValue):
        n = len(self.__data)
        
        # Insertion sort #
        if n <= 0:
            self.__data.insert(n, element)
            return True

        # Note that this is not a full insertion sort, but a single pass
        # We are only comparing the priority levels, not the value itself
        while self.__data[n-1].get_level() > element.get_level():
            if n == 0:
                break
            n -= 1
        
        self.__data.insert(n, element)

        # Note that as it is a dynamic array, we will never run out of space.
        # Hence, always return true
        return True
    
    def dequeue(self):
        if len(self.__data) == 0:
            # TODO!!! Add error for this!
            pass
        dequeued_item = self.__data[0]
        del self.__data[0]
        return dequeued_item.get_data()

    def display(self):
        print("Current Queue: {")
        for item in self.__data:
            print(f"Item: {item.get_data()}     Priority level: {item.get_level()}", end=", ")
        print("\n}")

        print(f"Current queue length: {len(self.__data)}")
        
        
class CircularQueue(QueueInterface):
    def __init__(self, queue_len: int):
        self.__data = [QueueValue(None, 1)] * queue_len
        self.__max_len = queue_len
        self.__len = 0
        self.__front = 0
        self.__rear = -1

    def enqueue(self, element: QueueValue):
        if self.__len == self.__max_len:
            # TODO!!!
            print("Queue is full. Cannot enqueue.")
            return False
        
        self.__rear = (self.__rear + 1) % self.__max_len
        self.__data[self.__rear] = element
        self.__len += 1

        return True


    def dequeue(self):
        if self.__len == 0:
            # TODO!!! Add error for this!
            print("Queue is empty. Cannot dequeue.")
            return "Nothing"
        
        dequeued_item = self.__data[self.__front]
        # Queue is static, hence the data within the index doesn't change until needed
        # Hence, only shift the front pointer up once, and decrease queue length
        self.__front = (self.__front + 1) % (self.__max_len)
        self.__len -= 1
        return dequeued_item.get_data()
    
    def display(self):
        print("Current queue: {", end=" ")
        for item in self.__data:
            print(item.get_data(), end=", ")
        print("}")

        print(f"Front ptr: {self.__front}")
        print(f"Rear ptr: {self.__rear}")
        print(f"Current queue length: {self.__len}    Max queue length: {self.__max_len}")


## Inherits Circular queue, hence static ## 
class CircularPriorityQueue(CircularQueue):
    
    def insertion(self) -> bool:
        item_ptr = self.__rear
        if item_ptr == self.__front:
            return True
        
        start_ptr = self.__front
        cur_ptr = self.__rear
        
        while cur_ptr != start_ptr:
            if self.__data[cur_ptr] >= self.__data[(cur_ptr - 1) % self.__max_len]:
                return True
            
            cur_ptr -=1
                
        
        
        
    
    def enqueue(self, element: QueueValue):
        if self.__len == self.__max_len:
            print("Queue is full. Cannot enqueue.")
            return False
        
        
        self.__rear = (self.__rear + 1) % self.__max_len
        self.__data[self.__rear] = element
        self.__len += 1
        
        
        ## Insertion sort to sort the queue every item enqueue ##
        self.insertion()
        
        return True