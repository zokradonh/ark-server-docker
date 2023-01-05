
from pathlib import Path

class Location:
    def set_file(self, path: Path):
        self.file = path

    def set_in_file_path(self, path: str):
        '''Some additional path information for use in config files. Like section names in ini files or json/yaml member paths'''
        self.in_file_path = path

