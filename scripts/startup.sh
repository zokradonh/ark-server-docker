#!/bin/bash

set -e

if [ -z "$INSTANCE_NAME" ]
then
    echo "Please specify environment variable 'INSTANCE_NAME'"
    exit 1
fi

rm /etc/arkmanager/instances/*

touch /etc/arkmanager/instance.cfg

python3 /scripts/config_edit.py -f /etc/arkmanager/arkmanager.cfg -c /etc/arkmanager/arkmanager-changeset.cfg -s defaultinstance=${INSTANCE_NAME} configfile_${INSTANCE_NAME}=/etc/arkmanager/instance.cfg

#python3 /scripts/ark_env.py > /etc/arkmanager/instance.cfg

#exec arkmanager start @${INSTANCE_NAME}

cat /etc/arkmanager/arkmanager.cfg

echo "############"
echo "Contents of /etc/arkmanager/instance.cfg:"

cat /etc/arkmanager/instance.cfg

exit 1