import os
import re


name_regex = re.compile(r"^ARK(?P<type>[A-Z]*)_(?P<option>[a-zA-Z0-9_]+)$")

cfg = ""

# transform environment variable `ARKFLAG_ServerAdminPassword` with contents `swordfish`
# to string `arkflag_ServerAdminPassword="swordfish"`

for name, value in os.environ.items():
    match = name_regex.search(name)
    if match is None:
        continue
    cfg_name = f"ark{match.group('type').lower()}_{match.group('option')}"

    cfg += f'{cfg_name}="{value}"\n'

print(cfg)
