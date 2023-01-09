
import re

class Scheme():

    name : str

    subclasses = dict()

    subclasses : dict[str, type]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.name] = cls

    comment_symbol = "+"

    key_search_pattern = None
    key_search_pattern : re.Pattern

    def create_config_line(cls, key: str, value: str) -> str:
        pass

    def comment_line(cls, config: re.Match) -> str:
        return cls.comment_symbol + config.group(0)

    def uncomment_line(cls, config: re.Match) -> str:
        return cls.create_config_line(config.group('key'), config.group('value'))

    def is_commented(cls, config: re.Match) -> bool:
        return cls.comment_symbol in config.group('prefix')

class BashLike(Scheme):
    name = "bashlike"

    def __init__(self):
        self.comment_symbol = "#"
        self.key_search_pattern = re.compile(r'^(?P<prefix>(?:[^\S\r\n]*#*)*)(?P<key>[a-zA-Z0-9_-]+)\s*=\s*"?(?P<value>[^"]+)"?', re.MULTILINE)

    def create_config_line(self, key: str, value: str) -> str:
        return f'{key}="{value}"'