# Hass Backup

> Automatically create snapshots and store them offsite (selfhosted)

## About

I manage a couple of Home Assistant instances and wanted a simple, centralized backup solution. The server is a Flask application that you can run on Docker (your NAS for example) while the Home Assistant addon acts a client and sends the backup over. I have also created some special endpoints, so Home Assistant can poll for individual backup status.

## Server installation

1. I assume that you have Docker already running
1. Copy the `server` directory from inside hass-backup to your server
2. Use the included `docker-compose.yml` file to create the container
3. Add users by editing `config.yaml`

## Server endpoints

All endpoints will prompt for credentials which are stored in the `config.yaml` file. A user may have the `is_admin` in order to query other users backup status.

GET `/status` - Return the backup status for the logged in account. Users with the `is_admin` attribute may get any status by appending the `account` parameter to the query `/status?account=other@example.com`.
Response: ```{"account":"demo@example.com","backups":5,"days_ago":0,"latest_backup":"12.12.2020 00:21"}```

POST `/upload` - Allows the Home Assistant addon to upload snapshots. All backup will be stored in the `/uploads/<account>/` directory.

## Installation (Home Assistant Addon)

1. Add the add-ons repository to your Home Assistant instance: `https://github.com/IDmedia/hass-addons`.
1. Install the Hass Backup addon.
1. Configure the add-on with your host information and credentials
1. Use my automation examples for automating the backup process

## Configuration

|Parameter|Required|Description|
|---------|--------|-----------|
|`host`|Yes|The ip/domain to the server.|
|`port`|Yes|The port the server uses.|
|`username`|Yes|The Username as defined in config.yaml on the server |
|`password`|Yes|The matching password|

## Example: Daily backups at 2 AM

I've added the following automation to make a daily backup.

_configuration.yaml_
```yaml
automation:
  - alias: Daily Backup at 2 AM
    initial_state: true
    trigger:
      platform: time
      at: '2:00:00'
    action:
      - service: hassio.addon_start
        data:
          addon: a6620db0_hass_backup
```