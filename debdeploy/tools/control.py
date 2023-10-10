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

Contains a control file parser
Package(name: str, version: str, arch: str, modifier: str) - Creates package instance
Control(control: list[str]) - Creates control instance
"""
import copy
import re
from debdeploy.tools.version import version_compare

from debdeploy.tools import definitions
from debdeploy import tools


# pylint: disable=[too-few-public-methods]
class Package:
    """
    Class, what defines package with it name, version, and, if defined, arch.
    Useful for defining package in any depend.
    __str__ return a string representation of package as described in dpkg documentation
    (such as "package:arch (modifier version )")
    __eq__ checks that package attributes name, arch and version are equal to each other
    check_version checks if package can be dependency.
    """

    def __init__(self, name: str, version=None, arch=None, modifier=None) -> None:
        self.name = name
        self.version = version.strip() if version is not None else None
        self.arch = arch
        self.modifier = modifier

    def __str__(self):
        return f"{self.name}\
{':'+self.arch if self.arch is not None else ''}\
{f' ({self.modifier} '+self.version+' )' if self.version is not None else ''}"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Package):
            return False
        isversion = True
        if __value.version is not None and self.version is not None:
            isversion = __value.version == self.version
        isarch = True
        if __value.arch is not None and self.arch is not None:
            isarch = __value.arch == self.arch
        # Name can't be None
        return __value.name == self.name and isarch and isversion

    def check_version(self, package, no_panic_return: bool = False) -> None:
        """
        Check if package can be dependency.
        This package contains modifier, given package contains version
        If in given package have modifier, it will ignored
        If this package haven't got modifier, raise exception NoPackageModifierError
        """
        if self.modifier is None:  # We don't need check version
            # It will also be None
            tools.printf(
                "This package doesn't contain modyfier or version, \
Can't check package compatibility!",
                level="f",
                exception=definitions.NoPackageModifierError,
                check=no_panic_return,
            )
            return True  # May be it's true, because it
            # may not be original version, but package is required
        if not isinstance(package, Package):
            tools.printf(
                f"Can't use '{package}' as Package object!",
                level="f",
                exception=TypeError,
                check=no_panic_return,
            )
            return None
        if package.version is None:
            tools.printf(
                f"Can't determine version of '{package}'!",
                level="f",
                exception=ValueError,
                check=no_panic_return,
            )
            return None
        if package.name != self.name:
            return False
        if (package.arch is not None and self.arch is not None) and (
            package.arch != self.arch
        ):
            return False
        compared = version_compare(package.version, self.version)
        return (
            compared == 0
            if self.modifier == "="
            else compared < 0
            if self.modifier == "<<"
            else compared > 0
            if self.modifier == ">>"
            else compared >= 0
            if self.modifier == ">="
            else compared <= 0
            if self.modifier == "<="
            else (
                tools.printf(
                    "Can't determine modifier!",
                    level="f",
                    exception=ValueError,
                    check=no_panic_return,
                )
                or False
            )
        )


class Control:
    """
    Main control file parser
    __eq__ checks that described in control file package is equal to another control package
    section_package_list(section: str) - Returns list of packages in given section (if there is)
    """

    def __init__(self, control: list[str]) -> None:
        """
        Initializes instance and parses control
        """
        self.sections = {}
        self.original = control
        self.lists = {}
        self.__init_sections_()
        # Should never broke, because it is default package sections
        self.version = self.sections["version"]
        self.arch = self.sections["architecture"]
        self.name = self.sections["package"]
        self.package = Package(self.name, self.version, self.arch, "=")

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Control):
            return False
        return self.package == __value.package

    def __init_sections_(self) -> None:
        latest = ""
        original = []
        for line in self.original:
            if re.match(definitions.CONTROL_SECTION_REGEX, line.strip()):
                section, data = line.strip().split(":", 1)
                latest = section.lower()
                self.sections[section.lower()] = data.strip()
            else:
                if latest != "":
                    self.sections[
                        latest
                    ] = f"{self.sections[latest]}\n{line.strip()}".strip()
            if latest != "status":
                original.append(line)
        self.original = original

    def section_package_list(self, section: str) -> list[Package]:
        """
        Returns copy of packages, in what section is package
        """
        if self.lists.get(section) is None:
            try:
                self.lists[section] = parse_packages(self.sections[section])
            except KeyError:
                self.lists[section] = []
        return self.lists[section]

    def __debug_info__(self) -> str:
        """
        Returns str with debug data
        """
        return self.original


def get_controls(package_name: str) -> list[Control]:
    """
    Finds control for package in status dpkg file
    """
    _control = []
    # pylint: disable=[invalid-name] # Need to ignore non snake case
    with open(definitions.DPKG_CACHE_STATUS, encoding="utf-8") as f:
        status = f.readlines()
    found = False
    _controls = []
    # pylint: disable=[invalid-name]
    for x in status:
        if x.strip().lower() == f"package: {package_name}":
            found = True
        if x.strip().lower() == "" and found:
            found = False
            _controls.append(copy.deepcopy(_control))
            _control = []
        if found:
            _control.append(x)
    return [Control(x) for x in _controls]


def parse_packages(line: str) -> list[Package, list[Package]]:
    """
    Parses line of packages into readable list of Package classes
    """

    def generate_package(all_data: str) -> Package:
        """
        Generates packages from package:arch (version)
        """
        package, *version = all_data.split(" ", 1)
        modifier, *version = (
            version[0].strip("()").split(" ", 1) if len(version) > 0 else (None,)
        )
        package, *arch = package.split(":", 1)
        return Package(
            package,
            version=version[0] if len(version) > 0 else None,
            arch=arch[0] if len(arch) > 0 else None,
            modifier=modifier,
        )

    raw = line.split(",")
    out = []
    for package in raw:
        group = package.strip().split("|")
        if len(group) == 1:
            group = generate_package(group[0])
        else:
            group = [generate_package(x.strip()) for x in group]
        out.append(group)
    return out
