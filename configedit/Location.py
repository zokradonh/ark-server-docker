
from pathlib import Path
from Schemes.Scheme import Scheme

class Location:
    def __init__(self):
        self.folder = Path(".")
        self.scheme_def : Scheme

    def set_file(self, path: Path):
        self.file = path

    def set_in_file_path(self, path: str):
        '''Some additional path information for use in config files. Like section names in ini files or json/yaml member paths'''
        self.in_file_path = path

    def set_scheme(self, scheme: str):
        self.scheme = scheme

    def copy(self):
        duplicate = Location()
        duplicate.file = self.file
        duplicate.in_file_path = self.in_file_path
        duplicate.folder = self.folder
        duplicate.scheme = self.scheme
        return duplicate

