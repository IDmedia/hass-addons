#!/bin/bash
set -e

CONFIG_PATH=/data/options.json
HA=/usr/bin/ha

# Variables passed to the addon
HOST=$(jq --raw-output ".host" $CONFIG_PATH)
PORT=$(jq --raw-output ".port" $CONFIG_PATH)
SSL=$(jq --raw-output ".ssl" $CONFIG_PATH)
USERNAME=$(jq --raw-output ".username" $CONFIG_PATH)
PASSWORD=$(jq --raw-output ".password" $CONFIG_PATH)

# Make sure all variables are configured
if [ -z "$HOST" ] || [ -z "$PORT" ] || [ -z "$SSL" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]
then
    echo "Please configure the addon before use"
    exit 1
fi

# Create the backup
echo "Creating backup ($(date +'%d.%m.%Y %H:%M'))"
slug=$(${HA} snapshots new --name="${name}" | cut -d' ' -f2)
echo "Backup created: ${slug}"

# Upload backup
if ${SSL} == true; then HTTP="https"; else HTTP="http"; fi
upload_url="${HTTP}://${HOST}:${PORT}/upload"
echo "Uploading ${slug}.tar to ${upload_url}"
curl -u ${USERNAME}:${PASSWORD} -X POST -m 1800 -s -F file=@"/backup/${slug}.tar" ${upload_url}

# Delete local backup
${HA} snapshots reload
echo "Deleting local backup: ${slug}"
${HA} snapshots remove ${slug}

echo "Backup process done!"
exit 0