
import re
from Schemes.Scheme import Scheme

class BashLike(Scheme):
    name = "bashlike"

    def __init__(self):
        self.comment_symbol = "#"
        self.key_search_pattern = re.compile(r'^(?P<prefix>(?:[^\S\r\n]*#*)*)(?P<key>[a-zA-Z0-9_-]+)\s*=\s*"?(?P<value>[^"]+)"?', re.MULTILINE)

    def create_config_line(self, key: str, value: str) -> str:
        return f'{key}="{value}"'