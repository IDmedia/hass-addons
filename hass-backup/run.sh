#!/usr/bin/with-contenv bashio

# Exit script on errors
set -e

CONFIG_PATH=/data/options.json
HA=/usr/bin/ha

# Variables passed to the addon
HOST=$(jq --raw-output ".host" $CONFIG_PATH)
USERNAME=$(jq --raw-output ".username" $CONFIG_PATH)
PASSWORD=$(jq --raw-output ".password" $CONFIG_PATH)

# Make sure all variables are configured
if [ -z "$HOST" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]
then
    echo "Please configure the addon before use"
    exit 1
fi

# Remove leftover backups
rm -f /backup/*.tar

# Create the backup
echo "Creating backup ($(date +'%d.%m.%Y %H:%M'))"
slug=$(${HA} backups new | cut -d' ' -f2)
echo "Backup created: ${slug}"

# Upload backup
upload_url="${HOST}/upload"
echo "Uploading ${slug}.tar to ${upload_url}"
curl -u ${USERNAME}:${PASSWORD} -X POST -m 7200 -s -F file=@"/backup/${slug}.tar" ${upload_url}

# Delete local backup
${HA} backups reload
echo "Deleting local backup: ${slug}"
${HA} backups remove ${slug}

echo "Backup process done!"
exit 0
