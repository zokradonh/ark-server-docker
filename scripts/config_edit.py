
import re
import os

import argparse

from pathlib import Path

parser = argparse.ArgumentParser("Config Editor")
parser.add_argument("-f","--file")
parser.add_argument("-c","--changes")
parser.add_argument("-s","--set", required=False, nargs="*")

args = parser.parse_args()

config_file = args.file
changes_file = args.changes

# using [^\S\r\n] instead of \s in the beginning since we do not want to delete double new lines
# Perl's \h would do the same but is not supported by Python

cfg_regex = re.compile(r'^[^\S\r\n]*(?P<key>[a-zA-Z0-9_-]+)\s*=\s*"?(?P<value>[^"]+)"?', re.MULTILINE)

def repl(m: re.Match):
    if m.group('key') in changes.keys():
        return f'{m.group("key")}="{changes[m.group("key")]}"'
    else:
        return m.group(0)

changes = dict()

# parse changes from changes file
with open(changes_file) as f:
    for index, line in enumerate(f):
        m = cfg_regex.search(line)
        if m is None:
            continue
        changes[m.group('key')] = m.group('value')

# TODO: parse changes from environment prefixed with CFG_*

# parse changes from command line if present
if args.set != None:
    for set in args.set:
        m = cfg_regex.search(set)
        if m is None:
            print('Error parsing set argument, please use format: key=value key2=value2')
            continue
        changes[m.group('key')] = m.group('value')

# change config file according to aggregated changes
with open(config_file) as f:
    content = f.read()

changed_content = cfg_regex.sub(repl, content)

with open(config_file, "w") as f:
    f.write(changed_content)