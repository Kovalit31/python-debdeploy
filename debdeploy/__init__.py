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

Root module of debeploy
DON'T USE TEST DIRECTORY!
"""

import argparse
import os

from . import tools

__version__ = "1.2.0b1"


def parse() -> argparse.Namespace:
    """
    Parses args
    """

    uuid = tools.gen_uuid()
    parser = argparse.ArgumentParser(
        description=f"""Debian package builder and deployer from dpkg cache

    debdeploy version {__version__}, Copyright (C) 2023 Kovalit31
    debdeploy comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions.

""",
        prog="debdeploy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Switch to debug mode", default=False
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Be verbose", default=False
    )
    parser.add_argument(
        "packages",
        nargs="+",
        help="List of packages to build",
        metavar="PACKAGE",
    )
    parser.add_argument(
        "--destination",
        "-D",
        default=tools.definitions.DEBDEPLOY_WORKDIR.format(uuid=uuid),
        help="Folder for saving builded packages",
    )
    parser.add_argument(
        "--cache",
        "-C",
        help="Cache directory",
        default=tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(uuid=uuid),
    )
    parser.add_argument(
        "--no-superuser",
        "-S",
        action="store_true",
        help="Run without root permission (for overriding). \n\
    Caution: it can be broke resulting package!",
        default=False,
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Forces build of packages (either it was broken)",
        default=False,
        action="store_true",
    )
    parser.add_argument("--arch", help="Default arch", default=tools.get_arch())
    parser.add_argument(
        "--dependencies",
        "-E",
        help="Build with dependencies",
        action="store_true",
        default=False,
    )
    return parser.parse_args()


def main(args: argparse.Namespace = None):
    """
    Main function of programm
    """
    args = args if args is not None else parse()
    tools.check_sudo(args.no_superuser)
    tools.check_debian_linux()
    package_enum = {
        "packages": tools.control.parse_packages(", ".join(args.packages)),
        "builded": [],
        "ignore": 0,
    }
    while len(package_enum["packages"]) > 0:
        cur_package: list[tools.control.Package] = package_enum["packages"][0]
        tools.printf(f"Preparing to build '{str(cur_package)}'...")
        if isinstance(cur_package, list):
            # Oh no, there is some pudding
            package_enum["ignore"] = len(cur_package) - 1
            package_enum["packages"] = cur_package + package_enum["packages"][1:]
            continue
        all_controls = tools.control.get_controls(cur_package.name)
        cur_control = get_current_control(
            all_controls, cur_package, need_ignore=package_enum["ignore"] > 0
        )
        if cur_control is None:
            package_enum["ignore"] -= 1
            package_enum["packages"].pop(0)
            continue
        if args.debug:
            tools.printf(f"{cur_control.__debug_info__()}", level="d")
        _package = tools.control.parse_packages(f"{str(cur_control.package)}")[0]
        tools.printf(f"Got package '{_package}'")
        if is_package_builded(package_enum["builded"], _package):
            package_enum["packages"].pop(0)
            if package_enum["ignore"] > 0:
                # Clear ignore packages
                for _ in range(package_enum["ignore"]):
                    package_enum["packages"].pop(0)
            package_enum["ignore"] = 0
            continue
        correct = cur_package.check_version(_package, no_panic_return=True)
        if correct is not None and not correct:
            tools.printf(
                f"Dumping info:\nCurrent package: {cur_package}\nGot package: {_package}\n\
Is Correct: {correct}",
                level="d",
                check=(not args.debug),
            )
            tools.printf(
                "It can't be satishfy dependencies, may be broke or \
not sucessful previous installation of package!",
                level="f",
                exception=tools.definitions.PackageNotFoundError,
                check=(args.force or package_enum["ignore"] > 0),
            )
            if package_enum["ignore"] > 0:
                package_enum["ignore"] -= 1
            package_enum["packages"].pop(0)
            continue
        build_driver(_package, cur_control, args.cache, args.destination)
        if package_enum["ignore"] > 0:
            # It is successful build, if build not panic
            for _ in range(package_enum["ignore"]):
                # We don't use full count of packages, because code
                # below delete one more item from packages
                package_enum["packages"].pop(0)
            package_enum["ignore"] = 0
        package_enum["packages"].pop(0)
        if args.dependencies:
            package_enum["packages"].extend(
                cur_control.section_package_list("depends")
                + cur_control.section_package_list("pre-depends")
            )
        package_enum["builded"].append(_package)


def get_current_control(
    all_controls: list[tools.control.Control], package_name: str, need_ignore=False
) -> tools.control.Control:
    """
    Get current control from all_controls by arch
    """
    if len(all_controls) == 0:
        tools.printf(
            f"I don't know, what you want to build instead '{package_name}'...",
            level="f",
            exception=tools.definitions.PackageNotFoundError,
            check=need_ignore,
        )
        return None
    for cur_control in all_controls:
        if cur_control.arch == tools.get_arch() or cur_control.arch == "all":
            break
    else:
        tools.printf(
            f"Can't guess control file from '{all_controls}'!",
            level="f",
            exception=NotImplementedError,
            check=need_ignore,
        )
        return None
    return cur_control


def build_driver(
    package: tools.control.Package,
    control: tools.control.Control,
    cache: str,
    destination: str,
) -> None:
    """
    Set up and build package
    """
    tools.printf(f"Coping files for '{package}'...")
    package_files = tools.files.get_files(package)
    tools.files.create_dirs(package, cache, destination)
    tools.files.copy_files_to_target(package_files, os.path.join(cache, package.name))
    control_file = os.path.join(cache, package.name, "DEBIAN", "control")
    with open(control_file, "w", encoding="utf-8") as _f:
        _f.write("".join(control.original))
    os.chmod(control_file, 0o0644)
    tools.build.build(package, cache, destination)


def is_package_builded(
    builded_list: list[tools.control.Package], package: tools.control.Package
) -> bool:
    """
    Checks if package is builded
    """
    for _x in builded_list:
        if _x == package:
            return True
    return False


# pylint: disable=[wrong-import-position]
from . import tests
