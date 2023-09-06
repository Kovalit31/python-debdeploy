'''
Main executable of debdeploy package
'''

import argparse
import os
import random
import string
from debdeploy.tools import control, files, build
from debdeploy import tools

def parse() -> argparse.Namespace:
    '''
    Parses args
    '''

    uuid = "".join(random.choices([*(string.ascii_lowercase+string.digits)],k=20))
    parser = argparse.ArgumentParser(
        description="Debian package builder and deployer from dpkg cache"
        )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Switch to debug mode",
        default=False
        )
    parser.add_argument(
        "-v",
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
        default=f"/tmp/debdeploy-{uuid}",
        help="Folder for saving builded packages"
    )
    parser.add_argument(
        "--cache",
        "-c",
        help="Cache directory",
        default=f"/tmp/debdeploy-{uuid}-cache"
    )
    parser.add_argument(
        "--no-root-perms",
        action="store_true",
        help="Run without root permission (for overriding). \n\
            Caution: it can be broke resulting package!",
        default=False
    )
    return parser.parse_args()

def main(args: argparse.Namespace):
    '''
    Main function of programm
    '''
    if not tools.check_sudo() and not args.no_root_perms:
        tools.printf("Programm can't be run without sudo.", level='f', exception=PermissionError)
    packages = [control.Package(x) for x in args.packages]
    for package in packages:
        _controls = control.get_controls(package)
        if len(_controls) > 1:
            tools.printf(
                "Parsing package with two controls (arches) not yet implemented!",
                level='f',
                exception=NotImplementedError
            )
        _control = _controls[0]
        # _package = control.Package(
        # package.package, version=curcontrol.version, arch=curcontrol.arch
        # )
        package_files = files.get_files(package)
        files.create_dirs(package, args.cache, args.destination)
        files.copy_files_to_target(package_files, os.path.join(args.cache, package.package))
        control_file = os.path.join(args.cache, package.package, "DEBIAN", "control")
        with open(control_file, 'w', encoding="utf-8") as _f:
            _f.write("".join(_control.original))
        os.chmod(control_file, 0o0644)
        build.build(package, args.cache, args.destination)

if __name__ == "__main__":
    main(parse())
