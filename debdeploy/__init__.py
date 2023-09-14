'''
Root module of debeploy
DON'T USE TEST DIRECTORY!
Imports tools
'''

import argparse
import os
import random
import string

from . import tools

def gen_uuid(length=20) -> str:
    '''
    Generates uuid from digits and lowercase ascii letters
    '''
    return  "".join(random.choices([*(string.ascii_lowercase+string.digits)],k=length))

def parse() -> argparse.Namespace:
    '''
    Parses args
    '''

    uuid = gen_uuid()
    parser = argparse.ArgumentParser(
        description="Debian package builder and deployer from dpkg cache",
        prog="debdeploy"
        )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Switch to debug mode",
        default=False
        )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Be verbose",
        default=False
    )
    parser.add_argument(
        "packages",
        nargs="+",
        help="List of packages to build",
        metavar="PACKAGE",
        )
    parser.add_argument(
        "--destination",
        "-d",
        default=tools.definitions.DEBDEPLOY_WORKDIR.format(
            uuid=uuid
            ),
        help="Folder for saving builded packages"
    )
    parser.add_argument(
        "--cache",
        "-c",
        help="Cache directory",
        default=tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(
            uuid=uuid
            )
    )
    parser.add_argument(
        "--no-superuser",
        action="store_true",
        help="Run without root permission (for overriding). \n\
    Caution: it can be broke resulting package!",
        default=False
    )
    parser.add_argument(
        '-f',
        '--force',
        help="Forces build of packages (either it was broken)",
        default=False,
        action="store_true"
    )
    parser.add_argument(
        "--arch",
        help="Default arch",
        default=tools.get_arch()
    )
    parser.add_argument(
        "--dependencies",
        help="Build with dependencies",
        action="store_true",
        default=False
    )
    return parser.parse_args()

def main(args: argparse.Namespace):
    '''
    Main function of programm
    '''
    if not tools.check_sudo() and not args.no_superuser:
        tools.printf("Programm can't be run without sudo.", level='f', exception=PermissionError)
    packages = tools.control.parse_packages(", ".join(args.packages))
    builded = []
    ignore_count = 0
    while len(packages) > 0:
        package = packages[0]
        if isinstance(package, list):
            # Oh no, there is some pudding
            ignore_count = len(package) - 1
            packages = package + package[1:]
            continue
        _controls = tools.control.get_controls(package.name)
        if len(_controls) > 1:
            for _control in _controls:
                if _control.arch == tools.get_arch() or _control.arch == "all":
                    break
            else:
                tools.printf(
                    f"Can't guess control file from '{_controls}'!",
                    level='f',
                    exception=NotImplementedError,
                    check=(ignore_count > 0)
                )
                ignore_count -= 1
                packages.pop(0)
                continue
        if len(_controls) == 0:
            tools.printf(
                f"I don't know, what you want to build instead '{package.name}'...",
                level='f',
                exception=tools.definitions.PackageNotFoundError,
                check=(ignore_count > 0)
            )
            ignore_count -= 1
            packages.pop()
            continue
        _control = _controls[0]
        if args.debug:
            tools.printf(
                f"{_control.__debug_info__()}",
                level='d'
            )
        _package = tools.control.parse_packages(f"{_control.package}\
{f':{_control.arch}' if _control.arch is not None else ''}\
{f' (= {_control.version})' if _control.version is not None else ''}")[0]
        for _builded_package in builded:
            if package == _builded_package:
                packages.pop(0)
                if ignore_count > 0:
                    # Clear ignore_count packages
                    for _ in range(ignore_count):
                        packages.pop(0)
                ignore_count = 0
                continue
        correct = package.check_version(_package, no_panic_return=True)
        if correct is not None and not correct:
            tools.printf(
                "It can't be satishfy dependencies, may be broke or \
not sucessful previous installation of package!",
                level='f',
                exception=tools.definitions.PackageNotFoundError,
                check=(args.force or ignore_count > 0)
                )
            if ignore_count > 0:
                ignore_count -= 1
            packages.pop(0)
            continue
        package_files = tools.files.get_files(_package)
        tools.files.create_dirs(_package, args.cache, args.destination)
        tools.files.copy_files_to_target(package_files, os.path.join(args.cache, _package.name))
        control_file = os.path.join(args.cache, _package.name, "DEBIAN", "control")
        with open(control_file, 'w', encoding="utf-8") as _f:
            _f.write("".join(_control.original))
        os.chmod(control_file, 0o0644)
        tools.build.build(_package, args.cache, args.destination)
        if ignore_count > 0:
            # It is successful build, if build not panic
            for _ in range(ignore_count):
                # We don't use full count of packages, because code
                # below delete one more item from packages
                packages.pop(0)
            ignore_count = 0
        packages.pop(0)
        if args.dependencies:
            packages.extend(_control.depends() + _control.pre_depends())
        builded.append(package)

# pylint: disable=[wrong-import-position]
from . import tests
