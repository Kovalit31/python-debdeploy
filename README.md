# deb_deploy

Deb package builder and deployer from already installed packeges on Python3 for Debian-based GNU/Linux OS

## Requirments

No requirments at this moment, your requirment is only sudo and python3, what can installed by 'apt install python3 sudo'

## Usage

To build package, just start
'cd /path/to/deb_deploy/ && sudo python3 -m deb_deploy "package_name"'

## Defaults

Default path, where is saving debs and cache is '/tmp/DEBS' and '/tmp' equalent

## NOTE

This program can build package only if you have pre-installed this package in system. Messages about 'System damage' may caused by
broken packages, permantly deleted files of package (such as locales with bleachbit) utc.

Good luck!
