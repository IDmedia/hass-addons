# Hass Backup

> Automatically create backups and store them offsite (selfhosted)

## About

I manage a couple of Home Assistant instances and wanted a simple, centralized backup solution. The server is a Flask application that you can run on Docker (your NAS for example) while the Home Assistant addon acts a client and sends the backup over. I have also created some special endpoints, so Home Assistant can poll for individual backup status.

## Server installation

1. I assume that you have Docker already running
1. Copy the `server` directory from inside hass-backup to your server
2. Use the included `docker-compose.yml` file to create the container
3. Add users by editing `config.yaml`

## Server endpoints

All endpoints will prompt for credentials which are stored in the `config.yaml` file. A user may have the `is_admin` in order to query other users backup status.

GET `/status` - Return the backup status for the logged in account. Users with the `is_admin` attribute may get any status by appending the `account` parameter to the query `/status?account=user@example.com`.
Response: ```{"account":"demo@example.com","backups":5,"days_ago":0,"latest_backup":"12.12.2020 00:21"}```

POST `/upload` - Allows the Home Assistant addon to upload backups. All backups will be stored in the `/uploads/<account>/` directory.

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

## Example: Sensor for backup status

I've also created a sensor so I can monitor how many backups are stored on the server and when the last backup was taken.

_configuration.yaml_
```yaml
sensor:
  - platform: rest
    name: Backup status
    username: !secret backup_username
    password: !secret backup_password
    authentication: basic
    json_attributes:
      - account
    resource: http://192.168.1.50:8070/status # Or status?account=user@example.com
    scan_interval: 300
    value_template: '{{ value_json.days_ago }}'
```

## Example: Lovelace card

![Lovelace Card Example](lovelace_card_example.png "Lovelace Card Example")

Here is my lovelace card that I use. Please modify it to your liking. 
Note that it requires [lovelace_gen](https://github.com/thomasloven/hass-lovelace_gen).

_hass_backup_card.yaml_
```yaml
# lovelace_gen

type: "custom:button-card"
color_type: card
entity: {{ entity }}

{% if show_account == true %}
show_label: true
label: >
  [[[
    if (entity)
      return entity.attributes.account
    else
      return ''
  ]]]
{% endif %}

tap_action:
  action: none
styles:
  card:
    - height: 150px
    - color: white
  label:
    - font-size: 12px
    - padding-top: 4px
state:
  - value: 3
    operator: '<='
    {% if show_backup_age == false %}
    name: >
      [[[
        return 'Backup Completed'
      ]]]
    {% else %}
    name: >
      [[[
        if (entity.state == 0)
          return 'Backup Completed (Today)'
        else if (entity.state == 1)
          return 'Backup Completed (Yesterday)'
        else
          return `Backup Completed (${entity.state} days ago)`
      ]]]
    {% endif %}
    color: var(--label-badge-green)
    icon: mdi:cloud-lock
  - operator: default
    {% if show_backup_age == false %}
    name: >
      [[[
        return 'System Not Backed Up'
      ]]]
    {% else %}
    name: >
      [[[
        if(isNaN(entity.state))
          return `System Not Backed Up (${entity.state.charAt(0).toUpperCase() + entity.state.slice(1)})`
        else if (entity.state > 365)
          return 'System Not Backed Up (Never)'
        else
          return `System Not Backed Up (${entity.state} days ago)`
      ]]]
    {% endif %}
    color: var(--label-badge-red)
    icon: mdi:cloud-alert
```

Usage:
_ui-lovelace.yaml_
```yaml
type: vertical-stack
cards:
  - !include
    - hass_backup_card.yaml
    - entity: sensor.backup_status
  - type: horizontal-stack
    cards:
      - !include
        - hass_backup_card.yaml
        - entity: sensor.backup_status_instance_2
          show_backup_age: false
          show_account: true
          
      - !include
        - hass_backup_card.yaml
        - entity: sensor.backup_status_instance_3
          show_backup_age: false
          show_account: true
```
