#!/usr/bin/env python3

import re
import os

import argparse

from occ.ConfigEditor import ConfigEditor

from pathlib import Path

if os.environ.get('INSTANCE_NAME') == None:
    print("Please specify environment variable 'INSTANCE_NAME'")
    exit(1)

instance_name = os.environ.get('INSTANCE_NAME')

# ex 27000:27000/udp
port_regex = re.compile(r"(\d+):(\d+)(/((udp)|(tcp)))?$")
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

def exit_on_nonzero(result: int):
    if result != 0:
        exit(result)

parser = argparse.ArgumentParser("Config Editor")

arkmanager_config_folder = Path("/etc/arkmanager")
arkmanager_config = arkmanager_config_folder / "arkmanager.cfg"
arkmanager_instance_config = arkmanager_config_folder / "instance.cfg"

args = parser.parse_args()

# delete all instance config files
exit_on_nonzero(os.system("rm /etc/arkmanager/instances/*"))

editor = ConfigEditor()

# debug
editor.debug = 1
# debug
#editor.output_file_suffix = ".new.cfg"

# parse changes from changeset file
changes = editor.parse_changeset_file(arkmanager_config_folder / "arkmanager-changeset.cfg", "bashlike", arkmanager_config)

changes += editor.manual_setn("bashlike", arkmanager_config, {
    "defaultinstance": instance_name,
    f"configfile_{instance_name}": str(arkmanager_instance_config),
})

steamport = parse_port("STEAMPORT")
gameport = parse_port("GAMEPORT")

changes += editor.manual_setn("bashlike", arkmanager_instance_config, {
    "arkserverroot": "/ark/server",
    f"configfile_{instance_name}": str(arkmanager_instance_config),
    "ark_QueryPort": steamport,
    "ark_Port": gameport
})

# parse changes from environment
changes += editor.parse_env()

# change configuration file
editor.change_config(changes)