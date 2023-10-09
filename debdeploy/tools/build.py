'''

    debdeploy - Build dpkg package and it dependencies from dpkg cache
    Copyright (C) 2023 Kovalit31

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

Package main builder
build(package: control.Package, cache_dir: str, dest_dir: str) -
Builds package in dest_dir from cache_dir
execute(cmd: str) - Wrap around os.system()
'''
import os

from debdeploy import tools
from debdeploy.tools import control, definitions

def build(package: control.Package, cache_dir: str, dest_dir: str) -> None:
    '''
    Builds package in dest_dir from cache_dir
    '''
    if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
        tools.printf(f"Directory is not a directory: '{dest_dir}'!")
    tools.printf(f"Building package {str(package)}")
    _code = execute(
        f"sudo dpkg-deb -Sextreme -b {os.path.join(cache_dir, package.name)} \
{os.path.join(dest_dir, f'{package.name}_{package.version}_{package.arch}.deb')}"
        )
    if _code == 0:
        return
    tools.printf("Error building package! Consider install dpkg-dev package!" if _code == 127
                 else "Build error!" ,
                 level='f',
                 exception=definitions.NotSupportedSystemError if _code == 127
                   else definitions.PackageBuildError)

def execute(cmd: str) -> int:
    '''
    Wrap around os.system()
    '''
    print(cmd)
    code = os.system(cmd)
    code = code >> 8
    return code
