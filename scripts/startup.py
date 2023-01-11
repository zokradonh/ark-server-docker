#!/usr/bin/env python3

import re
import os
import subprocess
import sys
import argparse

from occ.ConfigEditor import ConfigEditor

from pathlib import Path

instance_name = os.environ.get('INSTANCE_NAME')
utility = os.environ.get('UTILITY')

if utility:
    instance_name = "main"

if instance_name == None:
    print("Please specify environment variable 'INSTANCE_NAME'")
    exit(1)

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

def runf(command: str):
    result = run(command)
    if result != 0:
        exit(result)
    return result

def run(command: str):
    process = subprocess.Popen(args=command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    return process.returncode

parser = argparse.ArgumentParser("Config Editor")

arkmanager_config_folder = Path("/etc/arkmanager")
arkmanager_config = arkmanager_config_folder / "arkmanager.cfg"
arkmanager_instance_config = arkmanager_config_folder / "instance.cfg"

args = parser.parse_args()

# delete all instance config files
runf("rm /etc/arkmanager/instances/*")

editor = ConfigEditor()

# debug
editor.debug = 1
# debug
#editor.output_file_suffix = ".new.cfg"

# parse changes from changeset file
changes = editor.parse_changeset_file(arkmanager_config_folder / "arkmanager-changeset.cfg", "bashlike", arkmanager_config)

# set basic instance configuration
changes += editor.manual_setn("bashlike", arkmanager_config, {
    "defaultinstance": instance_name,
    f"configfile_{instance_name}": str(arkmanager_instance_config),
})

if utility:
    steamport = 27000
    gameport = 17000
else:
    steamport = parse_port("STEAMPORT")
    gameport = parse_port("GAMEPORT")

changes += editor.manual_setn("bashlike", arkmanager_instance_config, {
    f"configfile_{instance_name}": str(arkmanager_instance_config),
    "ark_QueryPort": steamport,
    "ark_Port": gameport
})

# parse changes from environment
changes += editor.parse_env()

# change configuration file
editor.change_config(changes)

if os.environ.get('UTILITY') == "update":
    runf("chown -R steam:steam /ark")

    if Path("/ark/server/ShooterGame").exists() and Path("/ark/server/version.txt").exists():
        runf("arkmanager installmods")
        os.execlp("arkmanager", "arkmanager", "update","--update-mods")
    else:
        runf("arkmanager install --verbose")
        os.execlp("arkmanager", "arkmanager", "installmods")
elif os.environ.get('UTILITY', "no") != "no":
    # check if game is installed and fail if not
    if not Path("/ark/server/version.txt").exists():
        print("ARK Survival Evolved server files are not installed. Please run this container with 'update' command.")
        exit(1)

    instance_name = os.environ.get('INSTANCE_NAME')

    # start game server and replace python process
    os.execlp("arkmanager", "arkmanager", "run", instance_name)