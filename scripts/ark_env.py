import os
import re

# All environment variables prefixed with "ARK" are read by this script

# ARKOPT_clusterid ARK_ServerAdminPassword
name_regex = re.compile(r"^ARK(?P<type>[A-Z]*)_(?P<option>[a-zA-Z0-9_]+)$")

# 27000:27000/udp
port_regex = re.compile(r"(\d+):(\d+)(/((udp)|(tcp)))?$")

cfg = '''
arkserverroot="/ark"                                     # path of your ARK server files (default ~/ARK)
arkautorestartfile=ShooterGame/Saved/.autostart
'''[1:-1]

# transform environment variable `ARKFLAG_ServerAdminPassword` with contents `swordfish`
# to string `arkflag_ServerAdminPassword="swordfish"`

for name, value in os.environ.items():
    match = name_regex.search(name)
    if match is None:
        continue
    cfg_name = f"ark{match.group('type').lower()}_{match.group('option')}"

    cfg += f'{cfg_name}="{value}"\n'


def parse_port(env_name: str) -> int:
    portstr = os.environ.get(env_name)
    if portstr is None:
        print(f"Please specify environment variable '{env_name}'")
        exit(1)
    m = port_regex.search(portstr)
    if m is None:
        print(f"Please specify environment variable '{env_name}' in docker compose file port short syntax, e.g. '27000:27000/udp'")
        exit(1)
    return int(m.group(2))

steamport = parse_port("STEAMPORT")
cfg += f'ark_QueryPort="{steamport}"\n'

gameport = parse_port("GAMEPORT")
cfg += f'ark_Port="{gameport}"\n'

mapname = os.environ.get("MAP")
if mapname is None:
    print(f"Please specify environment variable 'MAP'")
    exit(1)

cfg += f'serverMap="{mapname}"\n'

print(cfg)
