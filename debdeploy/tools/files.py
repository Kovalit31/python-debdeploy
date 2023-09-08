'''
Work with package files
'''
import os
import re
import shutil
from debdeploy.tools import definitions, control
from debdeploy import tools


def get_files(package: control.Package) -> list[str]:
    '''
    Get files from dpkg cache, what stores info about package
    '''
    # pylint: disable=[expression-not-assigned]
    files = os.listdir(definitions.DPKG_CACHE_INFO_FILES_ROOT)
    package_files = {}
    archs = []
    for _x in files:
        if re.match(definitions.PACKAGE_INFO_FILE_REGEX.format(package=package.name),
                    _x):
            if ":" in _x:
                arch = _x.split(".")[0].split(":", 1)[1]
            else:
                arch = "default"
            if arch in archs:
                package_files[arch].append(_x)
            else:
                package_files[arch] = [_x]
                archs.append(arch)
    if len(package_files) == 0:
        tools.printf(
            "Info files for this package can't be found!",
            level='f',
            exception=definitions.PackageNotFoundError
        )
    if len(package_files) > 1:
        tools.printf(
            "Two arches have not supported yet!",
            level='f',
            exception=NotImplementedError
        )
    return package_files[archs[0]]

def copy_files_to_target(files: list[str], target: str) -> None:
    '''
    Copyies files to target directory
    '''
    # pylint: disable=[expression-not-assigned]
    if not os.path.isdir(target) and os.path.exists(target):
        tools.printf(
            f"Path to save package data is not directory: '{target}'!",
            level="f",
            exception=NotADirectoryError
        )
    metadata = os.path.join(target, "DEBIAN")
    package_list = os.path.join(metadata, "list")
    for _x in files:
        shutil.copy2(os.path.join(definitions.DPKG_CACHE_INFO_FILES_ROOT, _x),
                         os.path.join(metadata, _x.split(".")[1]),
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
                level='w',
                check=warn
            )
            tools.printf(f"{file.strip()}", level='c')
            warn = True
            continue
        if os.path.isdir(file.strip()):
            tools.force_makedirs(destination)
            shutil.copystat(file.strip(), destination)
            continue
        shutil.copy2(file.strip(), destination)
    os.remove(package_list)
    to_chmod = []
    for _mfile in os.listdir(metadata):
        if re.match(definitions.SCRIPTS, _mfile):
            to_chmod.append(os.path.join(metadata, _mfile))
    (os.chmod(x, 0o0755) for x in to_chmod)

def create_dirs(package: control.Package, cache_dir: str, dest_dir: str) -> None:
    '''
    Creates dirs for build
    '''
    package_workdir = os.path.join(cache_dir, package.name)
    package_controldir = os.path.join(package_workdir, "DEBIAN")
    # Create dirs
    tools.force_makedirs(cache_dir)
    tools.force_makedirs(dest_dir)
    tools.force_makedirs(package_workdir)
    tools.force_makedirs(package_controldir, mode=0o0755)
