import subprocess

import sys

def run(command: list[str]):
    process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    return process.returncode

run(["arkmanager","--help"])

#print(len(sys.argv))

# if [ ! -d /ark/server/ShooterGame  ] || [ ! -f /ark/server/version.txt ]; then
#     echo "No game files found. Installing..."
#     chown -R steam:steam /ark
#     arkmanager install
#     arkmanager installmods
# else
#     arkmanager installmods
#     arkmanager update --update-mods
# fi
