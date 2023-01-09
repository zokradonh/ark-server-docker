
import os
import re

from pathlib import Path
import urllib.parse

from Location import Location
from Operations import *

oc_regex = re.compile(r'^OC_(?P<setting>[A-Z0-9_]+)$')
occ_regex = re.compile(r'^OCC_((?P<filename>[A-Z0-9][A-Z0-9_]+)__)?(?P<key>[A-Za-z0-9_]+)$')
ocl_regex = re.compile(r'^OCL_(?P<key>[A-Za-z0-9_]+)$')

class EnvParser:
    def __init__(self):
        self.base_location = Location()

        # first read and set settings
        for name, value in os.environ.items():
            if m := oc_regex.search(name):
                self.set_setting(m.group('setting'), value)
                continue

        self.operations = []
        self.operations : list[Operation]

        for name, value in os.environ.items():
            if m := occ_regex.search(name):
                l = self.base_location.copy()
                if m.group('filename'):
                    l.set_file(Path(m.group('filename')))
                if not l.file:
                    raise OccEnvError("Please provide file information by 'OC_FOLDER' or 'OC_FILE'. If you provided 'OC_FOLDER' then also specify file in 'OCC_<filename>__<key>=<value>'.")
                if not l.scheme:
                    raise OccEnvError("Please provide scheme information by 'OC_SCHEME' (e.g. OC_SCHEME=bashlike).")
                o = EditOrAdd(l, m.group('key'), value)
                self.operations.append(o)
                continue
            
            if m := ocl_regex.search(name):
                components = urllib.parse.urlparse(value)
                if not components.scheme.startswith("occ"):
                    continue
                if components.scheme.startswith("occ+") and len(components.scheme) > 4:
                    cscheme = components.scheme[4:]
                else:
                    if self.base_location.scheme:
                        cscheme = self.base_location.scheme
                    else:
                        raise OccEnvError("Please provide scheme information by 'OC_SCHEME' (e.g. OC_SCHEME=bashlike) or provide scheme in long syntax url (e.g. 'occ+bashlike:/file/path').")
                filename = components.path
                l = Location()
                l.set_file(filename)
                l.scheme = cscheme

                qsparts = urllib.parse.parse_qs(components.query, keep_blank_values=True)
                key = qsparts.get('k') or qsparts.get('key')

                # TODO: parse key for any in_file_path information

                if newvalue := qsparts.get('v') or qsparts.get('value'):
                    o = EditOrAdd(l, key, newvalue)
                    self.operations.append(o)
                if comment := qsparts.get('c') or qsparts.get('comment'):
                    o = Comment(l, key)
                    self.operations.append(o)
                if uncomment := qsparts.get('u') or qsparts.get('uncomment'):
                    o = Uncomment(l, key)
                    self.operations.append(o)
                if remove := qsparts.get('r') or qsparts.get('remove'):
                    o = Remove(l, key)
                    self.operations.append(o)


    def set_setting(self, setting_name: str, setting_value: str):
        if setting_name == "FOLDER":
            self.folder = Path(setting_value)
        if setting_name == "FILE":
            path = Path(setting_value)
            if self.folder:
                path = self.folder / path
            self.base_location.set_file(path)
        if setting_name == "SCHEME":
            self.base_location.scheme = setting_value

class OccEnvError(Exception):
    pass