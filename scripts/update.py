#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path

def runf(command: str):
    result = run(command)
    if result != 0:
        exit(result)
    return result

def run(command: str):
    process = subprocess.Popen(args=command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    return process.returncode

if os.environ.get('UTILITY') != "update":
    exit(0) # don't update, skip this init script

runf("chown -R steam:steam /ark")

if Path("/ark/server/ShooterGame").exists() and Path("/ark/server/version.txt").exists():
    runf("arkmanager installmods")
    runf("arkmanager update --update-mods")
else:
    runf("arkmanager install --verbose")
    runf("arkmanager installmods")
