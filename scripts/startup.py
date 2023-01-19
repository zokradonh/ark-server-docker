#!/usr/bin/env python3

import re
import os, pwd, grp
import subprocess
import sys
import argparse
import json
from collections import Counter

from occ.ConfigEditor import ConfigEditor, Operation

from pathlib import Path

instance_name = os.environ.get('INSTANCE_NAME')
utility = os.environ.get('UTILITY')

if utility:
    instance_name = "main"

if instance_name == None:
    print("Please specify environment variable 'INSTANCE_NAME'")
    exit(1)

arkmanager_config_folder = Path("/etc/arkmanager")
arkmanager_config = arkmanager_config_folder / "arkmanager.cfg"
arkmanager_instance_config = arkmanager_config_folder / "instance.cfg"
ark_mod_folder = Path("/ark/server/ShooterGame/Content/Mods/")
logs_folder = Path("/ark/logs/")
logs_instance_folder = logs_folder / f"{instance_name}.arktools"

os.makedirs(logs_instance_folder, exist_ok=True)

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

def get_required_mods(changes):
    for o in changes:
        o : Operation
        if o.key == "ark_GameModIds":
            return list(map(str.strip, o.value.split(',')))
    return []

def get_installed_mods():
    for dir in ark_mod_folder.iterdir():
        if dir.is_dir():
            yield dir.name

# from https://stackoverflow.com/a/2699996
# user https://stackoverflow.com/users/156771/tam%c3%a1s
# user https://stackoverflow.com/users/60075/craig-mcqueen
def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    passwd = pwd.getpwnam(uid_name)
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups(os.getgrouplist(passwd.pw_name, passwd.pw_gid))

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(passwd.pw_uid)

    # Set Home
    os.environ['HOME'] = passwd.pw_dir

parser = argparse.ArgumentParser("Config Editor")

args = parser.parse_args()

# delete all instance config files
if any(Path("/etc/arkmanager/instances/").iterdir()):
    runf("rm /etc/arkmanager/instances/*")

editor = ConfigEditor()

# debug
#editor.debug = 1
# debug
#editor.output_file_suffix = ".new.cfg"

# parse changes from changeset file
changes = editor.parse_changeset_file(arkmanager_config_folder / "arkmanager-changeset.cfg", "bashlike", arkmanager_config)

# set basic instance configuration
changes += editor.manual_setn("bashlike", arkmanager_config, {
    "defaultinstance": instance_name,
    "logdir": logs_instance_folder,
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

# ensure /ark and all world saves can be written
runf("chown -R steam:steam /ark")

if os.environ.get('UTILITY') == "update":
    if Path("/ark/server/ShooterGame").exists() and Path("/ark/server/version.txt").exists():
        runf("arkmanager installmods")
        os.execlp("arkmanager", "arkmanager", "update","--update-mods")
    else:
        # install game
        runf("arkmanager install --verbose")

        # backup default server config files
        runf("tar cfz /ark/defaultconfig.tgz /ark/server/ShooterGame/SavedArk/Config/LinuxServer/*")

        # install required mods
        os.execlp("arkmanager", "arkmanager", "installmods")
elif os.environ.get('UTILITY', "no") == "no":
    # check if game is installed and fail if not
    if not Path("/ark/server/version.txt").exists():
        print("ARK Survival Evolved server files are not installed. Please run this container with 'update' command.")
        exit(1)
    
    # check mods
    mods = get_required_mods(changes)
    installed_mods = list(get_installed_mods())
    if not set(mods) <= set(installed_mods):
        run(f"echo Instance '{instance_name}' has uninstalled mods.")
        runf("arkmanager installmods --verbose")

    # avoid runuser process
    drop_privileges("steam","steam")

    # start game server and replace python process
    os.execlp("arkmanager", "arkmanager", "run", f"@{instance_name}")