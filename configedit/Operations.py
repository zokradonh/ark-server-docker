import re

from Location import Location

class Operation:
    def __init__(self, location: Location, key: str, value: str):
        self.location = location
        self.key = key
        self.value = value

    def apply(self, m: re.Match):
        pass

class Edit(Operation):
    def apply(self, m: re.Match):
        return self.location.scheme_def.create_config_line(self.key, self.value)

class EditOrAdd(Operation):
    def apply(self, m: re.Match):
        return self.location.scheme_def.create_config_line(self.key, self.value)

class Add(Operation):
    def apply(self, m: re.Match):
        return self.location.scheme_def.create_config_line(self.key, self.value)

class Remove(Operation):
    def __init__(self, location: Location, key: str):
        self.location = location
        self.key = key
        self.value = None
    
    def apply(self, m: re.Match):
        return ""

class Comment(Operation):
    def __init__(self, location: Location, key: str):
        self.location = location
        self.key = key
        self.value = None

    def apply(self, m: re.Match):
        return self.location.scheme_def.comment_line(m)

class Uncomment(Operation):
    def __init__(self, location: Location, key: str):
        self.location = location
        self.key = key
        self.value = None

    def apply(self, m: re.Match):
        return self.location.scheme_def.uncomment_line(m)