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

Test debdeploy.tools.build
"""
import os
import shutil

from ..tools import build
from ..tools import control
from ..tools import gen_uuid

DIRNAME = os.path.dirname(__file__)
PACKAGE = os.path.join(DIRNAME, "example")


def test_build():
    """
    Test build function
    """
    uuid = gen_uuid()
    base = os.path.join("/", "tmp", f"test-{uuid}")
    cache = os.path.join(base, "cache")
    destination = os.path.join(base, "dest")
    os.makedirs(cache)
    os.makedirs(destination)
    shutil.copytree(PACKAGE, os.path.join(cache, "example"))
    build.build(control.Package("example"), cache, destination)


def test_execute():
    """
    Test execute function
    """
    code = build.execute("echo Hello!")
    assert code == 0, "You have incorrectly configured system!"
    code = build.execute(gen_uuid(length=50))
    print(code)
    assert code == 127, "You have incorrectly configured system!"
