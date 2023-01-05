
from . import *

class Operation:
    def __init__(self, location: Location, key: str, value: str):
        self.location = location
        self.key = key
        self.value = value

class Edit(Operation):
    pass

class EditOrAdd(Operation):
    pass

class Add(Operation):
    pass

class Remove(Operation):
    pass

class Comment(Operation):
    pass

class Uncomment(Operation):
    pass