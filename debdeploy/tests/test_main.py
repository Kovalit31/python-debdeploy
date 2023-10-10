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

Main programm tester
"""

import random

from argparse import Namespace

from .. import main
from .. import get_current_control
from .. import is_package_builded
from .. import tools

PACKAGES = [
    "apt",
    "dpkg",
    "libc6",
    "tar",
    "python3",
]


def create_namespace(*_, **kwargs):
    """
    Creates Namespace object to pass
    it as a string
    """
    return Namespace(**kwargs)


def random_choose_package():
    """
    Randomly chooses packages to build :)
    """
    return random.choice(PACKAGES)


def __test_main(packages: list[str], dependencies=False, force=False):
    """
    Test main (global tester)
    """
    uuid = tools.gen_uuid()
    destination = tools.definitions.DEBDEPLOY_WORKDIR.format(uuid=uuid)
    cache = tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(uuid=uuid)
    main(
        create_namespace(
            no_superuser=True,
            destination=destination,
            cache=cache,
            packages=packages,
            debug=True,
            dependencies=dependencies,
            force=force,
        )
    )


def test_main_single():
    """
    Test without dependencies with single package
    """
    __test_main([random_choose_package()])


def test_main_single_depends():
    """
    Test using build dependencies
    """
    __test_main([random_choose_package()], dependencies=True)


def test_main_lots():
    """
    Test without dependencies with many packages
    """
    __test_main(PACKAGES)


def test_main_lots_depends():
    """
    Test with many packages with dependencies
    """
    __test_main(PACKAGES, dependencies=True)


## Not using force, because it is tests!


def test_is_package_builded():
    """
    Test if package is builded
    """
    name = random_choose_package()
    assert is_package_builded(
        [tools.control.Package(name=name, version="2.0.0")],
        tools.control.Package(name=name, version="2.0.0"),
    )
    assert not is_package_builded(
        [tools.control.Package(name=name, version="2.0.0")],
        tools.control.Package(name=name, version="1.0.0"),
    )


def test_get_current_control():
    """
    Test get current control
    """
    control = tools.control.Control(
        [
            "Package: apt\n",
            "Status: ok installed\n",
            "Architecture: amd64\n",
            "Version: 2.0.0\n",
            "Maintainer: <NAME> <<EMAIL>>\n",
        ]
    )
    control_two = tools.control.Control(
        [
            "Package: apt\n",
            "Status: ok installed\n",
            "Architecture: i386\n",
            "Version: 2.0.0\n",
            "Maintainer: <NAME> <<EMAIL>>\n",
        ]
    )
    assert control == get_current_control([control, control_two], "apt")
