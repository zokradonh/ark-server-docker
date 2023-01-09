
import re
import os

import argparse

from configedit.ConfigEditor import ConfigEditor

from pathlib import Path

parser = argparse.ArgumentParser("Config Editor")
parser.add_argument("-f","--file")
parser.add_argument("-c","--changes")
parser.add_argument("-s","--set", required=False, nargs="*")

args = parser.parse_args()

config_file = args.file
changeset_file = args.changes


# using [^\S\r\n] instead of \s in the beginning since we do not want to delete double new lines
# Perl's \h would do the same but is not supported by Python

cfg_regex = re.compile(r'^[^\S\r\n]*(?P<key>[a-zA-Z0-9_-]+)\s*=\s*"?(?P<value>[^"]+)"?', re.MULTILINE)

editor = ConfigEditor()
editor.debug = 1

# parse changes from changeset file
changes = editor.parse_changeset_file(Path(changeset_file), "bashlike", Path(config_file))

# parse changes from command line if present
cmdline_changes = dict()
if args.set != None:
    for set in args.set:
        m = cfg_regex.search(set)
        if m is None:
            print('Error parsing set argument, please use format: key=value key2=value2')
            continue
        cmdline_changes[m.group('key')] = m.group('value')
changes += editor.manual_setn("bashlike", Path(config_file), cmdline_changes)

# parse change from environment
changes += editor.parse_env()

# change configuration file
editor.change_config(changes)
