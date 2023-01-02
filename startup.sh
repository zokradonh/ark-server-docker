#!/bin/bash

python3 /scripts/ark_env.py > /arkmanager-my.cfg

exec arkmanager start @${INSTANCE_NAME}