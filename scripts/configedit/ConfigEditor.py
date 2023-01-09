
import re
from pathlib import Path
import urllib.parse

from .Schemes import *

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
        duplicate.scheme_def = self.scheme_def
        return duplicate

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

class ConfigEditor:

    def __init__(self):
        pass

    def parse_env(self) -> list[Operation]:
        parser = EnvParser()
        return parser.operations

    def parse_changeset_file(self, file: Path, scheme: str, target_file: Path):
        if scheme not in Scheme.subclasses.keys():
            raise ValueError(f"Scheme '{scheme}' not supported.")

        operations = []

        with open(file) as f:
            content = f.read()
            l = Location()
            l.set_file(target_file)
            l.set_scheme(scheme)

            scheme_cls = Scheme.subclasses[scheme]
            scheme_cls : type[Scheme]

            for m in scheme_cls.key_search_pattern.finditer(content):
                o = EditOrAdd(l, m.group('key'), m.group('value'))
                operations.append(o)

            return operations

    def change_config(self, operations: list[Operation]):
        schemes = Scheme.subclasses

        files = []
        files : list[ConfigFile]

        for o in operations:
            if o.location.scheme:
                if scheme := schemes[o.location.scheme]:
                    o.location.scheme_def = scheme
            if o.location.file:
                for file in files:
                    if file.path == o.location.file:
                        file.operations.append(o)
                        break
                else:
                    files.append(ConfigFile(o.location.file, o))

        for file in files:
            def replace(m: re.Match):
                for o in file.operations:
                    if o.key == m.group('key'):
                        return o.apply(m)
                return m.group(0) # return original string, no change

            with open(file.path) as f:
                content = f.read()
                (changed, num_changes) = file.operations[0].location.scheme_def.key_search_pattern.subn(replace, content)
            with open(file.path, "w") as f:
                f.write(changed)
            print(f"Changed configs in file '{file.path}': {num_changes}")

class ConfigFile:
    path = Path(".")
    operations = []
    operations : list[Operation]
    scheme : type[Scheme]

    def __init__(self, path: Path, operation: Operation):
        self.path = path
        self.operations.append(operation)





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


