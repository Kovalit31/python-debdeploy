'''
Work with package files
'''
import os
import re
import shutil
from debdeploy.tools import definitions, control
from debdeploy import tools

def get_files(package: control.Package, check_arch=False) -> list[str]:
    '''
    Get files from dpkg cache, what stores info about package
    '''
    # pylint: disable=[expression-not-assigned]
    files = os.listdir(definitions.DPKG_CACHE_INFO_FILES_ROOT)
    package_files = []
    for _x in files:
        if (re.match(
                    definitions.PACKAGE_INFO_FILE_REGEX.format(
                        package=package.package
                        ),
                    _x
                ) and not check_arch) or re.match(
                    definitions.PACKAGE_INFO_FILE_ARCH_REGEX.format(
                        package=package.package,
                        arch=package.arch
                        ),
                    _x
                ):
            package_files.append(_x)
    if len(package_files) == 0:
        tools.printf(
            "Info files for this package can't be found!",
            level='f',
            exception=definitions.PackageNotFoundError
        )
    return package_files

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
    try:
        os.makedirs(metadata)
    except OSError:
        shutil.rmtree(metadata)
        os.makedirs(metadata)
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
            os.makedirs(os.path.join(target, file.strip()[1:]), exist_ok=True)
            shutil.copystat(file.strip(), os.path.join(target, file.strip()[1:]))
            continue
        shutil.copy2(file.strip(), os.path.join(target, file.strip()[1:]))
    os.remove(package_list)
    to_chmod = []
    for _mfile in os.listdir(metadata):
        if re.match(definitions.SCRIPTS, _mfile):
            to_chmod.append(os.path.join(metadata, _mfile))
    (os.chmod(x, 0o0755) for x in to_chmod)
    os.chmod(metadata, 0o0755)
