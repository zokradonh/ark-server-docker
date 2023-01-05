
import re

class Scheme:

    comment_symbol = "+"

    key_search_pattern = re.compile(".")

    def create_config_line(self, key: str, value: str) -> str:
        pass

    def comment_line(self, config: re.Match) -> str:
        return self.comment_symbol + config.group(0)

    def uncomment_line(self, config: re.Match) -> str:
        return self.create_config_line(config.group('key'), config.group('value'))