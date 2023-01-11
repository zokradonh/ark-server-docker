#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path

if os.environ.get('UTILITY', "no") != "no":
    exit(0) # this is a utility container start so don't start game server

# check if game is installed and fail if not
if not Path("/ark/server/version.txt").exists():
    print("ARK Survival Evolved server files are not installed. Please run this container with 'update' command.")
    exit(1)

instance_name = os.environ.get('INSTANCE_NAME')

def runf(command: str):
    result = run(command)
    if result != 0:
        exit(result)
    return result

def run(command: str):
    process = subprocess.Popen(args=command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    return process.returncode

# start game server and replace python process
os.execl("arkmanager","run",instance_name)