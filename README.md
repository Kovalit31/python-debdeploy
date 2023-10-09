# python-debdeploy

Deb package builder and deployer from already installed packeges on Python3 for Debian-based GNU/Linux OS

## Requirments

'apt install python3 sudo'

## Installing

'pip3 install <https://github.com/Kovalit31/python-debdeploy/archive/refs/heads/main.zip>' (replace main with required branch)

## Usage

To build package, just start
'debdeploy &lt;package&gt;'
For help, run
'debdeploy --help'

## Defaults

Default path, where is saving debs and cache is '/tmp/debdeploy-&lt;random characters&gt;' and '/tmp/debdeploy-&lt;random characters&gt;-cache' equalent

## NOTE

This program can build package only if you have pre-installed this package in system. Messages about 'System damage' may caused by
broken packages, permantly deleted files of package (such as locales with bleachbit) utc.

Good luck!
