#!/bin/bash

set -e

if [ -z "$INSTANCE_NAME" ] then
    echo "Please specify environment variable 'INSTANCE_NAME'"
    exit 1

rm /etc/arkmanager/instances/*

python3 /scripts/config_edit.py -f /etc/arkmanager/arkmanager.cfg -c /etc/arkmanager/arkmanager-docker.cfg -s defaultinstance=${INSTANCE_NAME}

python3 /scripts/ark_env.py > /etc/arkmanager/instances/${INSTANCE_NAME}.cfg

exec arkmanager start @${INSTANCE_NAME}