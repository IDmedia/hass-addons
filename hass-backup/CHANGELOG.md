# Changelog
All notable changes to this project will be documented in this file.

## [v0.0.5] (2021-07-09)

- Remove server code from repo as Home Assistant seemed to complain about that being bundled with the addon

## [v0.0.4] (2021-01-13)

- Force deletion of leftover snapshots so the command does not fail if no snapshots exists

## [v0.0.3] (2021-01-13)

- Make sure any leftover snapshots are removed from Home Assistant
- Make sure the `LIMIT_BACKUPS` enviroment variable is parsed as an integer. Fixes backups not being deleted on the server

## [v0.0.2] (2020-12-12)

- The number of stored backups on the server can now be changed using the `LIMIT_BACKUPS` enviroment variable.

## [v0.0.1] (2020-12-11)

- Initial release
