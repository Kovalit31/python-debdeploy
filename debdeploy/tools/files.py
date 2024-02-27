"""

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

Work with package files
"""
import os
import re
import shutil
from debdeploy.tools import definitions, control, normalize_re
from debdeploy import tools


def get_files(package: control.Package, default_arch=tools.get_arch()) -> list[str]:
    """
    Get files from dpkg cache, what stores info about package
    """
    # pylint: disable=[expression-not-assigned]
    files = os.listdir(definitions.DPKG_CACHE_INFO_FILES_ROOT)
    package_files = {}
    archs = []
    for _x in files:
        if re.match(
            definitions.PACKAGE_INFO_FILE_REGEX.format(
                package=normalize_re(package.name)
            ),
            _x,
        ):
            if ":" in _x:
                arch = "".join(_x.split(".")[:-1]).split(":", 1)[1]
            else:
                arch = tools.get_arch()  # There is two ways:
                # If there is multiarch packgae (all targets)
                # It will added to arch specific and will be skiped
                # If there is a arch-specific package
                # It, by default, will be placed to arch and next
                # arch-specific will be with arch
                # It is because filesystems can't contain two files with
                # same names and path
            if arch in archs:
                package_files[arch].append(_x)
            else:
                package_files[arch] = [_x]
                archs.append(arch)
    if len(package_files) == 0:
        tools.printf(
            f"Info files for '{package.name}' package can't be found!",
            level="f",
            exception=definitions.PackageNotFoundError,
        )
    if len(package_files) > 1:
        if default_arch not in package_files:
            tools.printf(
                f"Can't guess default arch to build from '{archs}'!",
                level="f",
                exception=NotImplementedError,
            )
        return package_files[
            default_arch
        ]  # It may be arch speccific or multiarch... Umm...
    return package_files[archs[0]]


def copy_files_to_target(files: list[str], target: str) -> None:
    """
    Copyies files to target directory
    """
    # pylint: disable=[expression-not-assigned]
    if not os.path.isdir(target) and os.path.exists(target):
        tools.printf(
            f"Path to save package data is not directory: '{target}'!",
            level="f",
            exception=NotADirectoryError,
        )
    metadata = os.path.join(target, "DEBIAN")
    package_list = os.path.join(metadata, "list")
    for _x in files:
        shutil.copy2(
            os.path.join(definitions.DPKG_CACHE_INFO_FILES_ROOT, _x),
            os.path.join(metadata, _x.split(".")[-1]),
        )
    with open(package_list, "r", encoding="utf-8") as _f:
        files = _f.readlines()
    warn = False
    for file in files:
        if file.strip() == "/.":
            continue
        destination = os.path.join(target, file.strip()[1:])
        if not os.path.exists(file.strip()):
            tools.printf(
                "There is no file, what defined in list. May be it is broken system!",
                level="w",
                check=warn,
            )
            tools.printf(f"{file.strip()}", level="c")
            warn = True
            continue
        if os.path.isdir(file.strip()):
            tools.force_makedirs(destination)
            shutil.copystat(file.strip(), destination)
            continue
        if os.path.islink(file):
            print(f"{file} is link")
        shutil.copy2(file.strip(), destination)
    os.remove(package_list)
    to_chmod = []
    for _mfile in os.listdir(metadata):
        if re.match(definitions.SCRIPTS, _mfile):
            to_chmod.append(os.path.join(metadata, _mfile))
    (os.chmod(x, 0o0755) for x in to_chmod)


def create_dirs(package: control.Package, cache_dir: str, dest_dir: str) -> None:
    """
    Creates dirs for build
    """
    package_workdir = os.path.join(cache_dir, package.name)
    package_controldir = os.path.join(package_workdir, "DEBIAN")
    # Create dirs
    tools.force_makedirs(cache_dir)
    tools.force_makedirs(dest_dir)
    tools.force_makedirs(package_workdir)
    tools.force_makedirs(package_controldir, mode=0o0755)
