
import re

class Scheme():

    name : str

    subclasses = []

    subclasses : dict[str, type]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.name] = cls

    comment_symbol = "+"

    key_search_pattern = re.compile(".")

    def create_config_line(cls, key: str, value: str) -> str:
        pass

    def comment_line(cls, config: re.Match) -> str:
        return cls.comment_symbol + config.group(0)

    def uncomment_line(cls, config: re.Match) -> str:
        return cls.create_config_line(config.group('key'), config.group('value'))