
import re
from Operations import *
from EnvParser import EnvParser
from Schemes import *
from pathlib import Path

class ConfigEditor:

    def __init__(self):
        pass

    def parse_env(self) -> list[Operation]:
        parser = EnvParser()
        return parser.operations

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
