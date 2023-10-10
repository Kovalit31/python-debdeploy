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

Tools module. Contains tools for extracting and work with package files
"""
import os
import platform
import random
import re
import string


def check_sudo(ignore=False) -> None:
    """
    Checks for sudo permission
    If there isn't root, return False
    """
    if os.getuid() != 0:
        printf(
            "Programm can't be run without sudo.",
            level="f",
            exception=PermissionError,
            check=ignore,
        )


def printf(*message, level="i", exception=Exception, check=False):
    """
    Print meassage with small styling
    """
    if check:
        return
    level = level[0].lower()
    symbol = (
        "#"
        if level == "d"
        else "~"
        if level == "v"
        else "*"
        if level == "i"
        else "!"
        if level == "w"
        else "@"
        if level == "e"
        else "&"
        if level != "c"
        else "`"
    )
    out_msg = f"[{symbol}] {''.join(message)}".replace("\n", "\n[`] ")
    print(out_msg)
    if level == "f":
        # pylint: disable=[broad-exception-raised]
        raise exception(out_msg)


def force_makedirs(path: str, mode=None) -> None:
    """
    Forces making of directory @string path
    """
    if os.path.isfile(path):
        printf(f"Can't create dircetory, if it is file: '{path}'!", level="e")
        return
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            pass
    if mode is None:
        return
    os.chmod(path, mode)


def get_arch() -> str:
    """
    Gets arch of host machine
    """
    # pylint: disable=[implicit-str-concat]
    _a_re = [
        "i.86/i386",
        "x86_64/amd64",
        "s390x/s390x",
        "aarch64.*/arm64",
    ]  # Predefined
    arch = platform.machine()
    for _x in _a_re:
        pattern, repl = _x.split("/")
        arch = re.sub(pattern, repl, arch)
    return arch


def normalize_re(regex: str) -> str:
    """
    Normalizes regex characters
    """
    return regex.replace("+", "\\+")


def gen_uuid(length=20) -> str:
    """
    Generates uuid from digits and lowercase ascii letters
    """
    return "".join(
        random.choices([*(string.ascii_lowercase + string.digits)], k=length)
    )


def check_debian_linux() -> bool:
    """
    Checks that system is linux and it is debian linux
    """
    if not platform.system().lower().startswith("linux") and os.path.exists(
        os.path.join("/", "var", "lib", "dpkg")
    ):
        printf(
            "System not Debian GNU/Linux or distribution of it!\
Can't prroceed building of packages!",
            level="f",
            exception=definitions.PlatformNotSupportedError,
        )


# pylint: disable=[wrong-import-position]
from . import control, definitions, files, build, version
