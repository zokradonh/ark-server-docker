# ARK Survival Evolved Docker Server

Docker Image for ARK gameserver. With the following goals in mind:

- DRY
- Spinning up a new game server instance should be very easy
- Instance start up times should be as short as possible

## Features

- Multi ARK instance server to support different ARK maps
- Multi ARK cluster to have seperate networks of ARK maps
- Configure all `ark-server-tools`' configs via `OCC_*` environment variables in `compose.yaml`
- One container per instance
- Each instance container share the same game files volume
- Each instance has its own SavedArk volume
- (Optional) One container for WebAPI to control the server clusters (+docker socket proxy container due to security reasons)
- (Optional) One container for FTP daemon to access the GameUserSettings.ini/Game.ini or to download/upload backups

## Reasons

- One volume per container since there is no good possibility to differ between all the different `GameUserSettings.ini`s of the instances
- I always use python instead of bash to reduce WTF/m
- I developed a completely overkill omni-config-changer project inside this project because I will need it later for other projects
  - I did not upload it to pip, because rst is not md and elephants are most likely not green

## How to use FTP

FTP daemon does not have any default users that you can connect to. Please create two users for ini and backups:
```
docker compose exec ftp pure-pw useradd savedark -u 1000 -g 1000 -d /arks -m
docker compose exec ftp pure-pw useradd backup -u 1000 -g 1000 -d /ark/backups -m
```

## Paths in Container

- `/ark/server` installed gamefiles
- `/ark/backups` backups created by arkmanager
- `/ark/scripts` folder with helper Python script(s)