import os
import sys
import shutil
import deb_deploy.tools.create as crt
import deb_deploy.tools.check as chk

def main(args):
    version_have = False
    package_full = args[1].lstrip().rstrip().split(" ")
    if len(package_full) > 1:
        package, version = package_full[0:1]
        version_have = True
    else:
        package = package_full[0]
    chk.check_perms()
    print(f"[.] Preparing to build package '{package}'...")
    files = chk.check_and_return_info_files(package)
    arch, files = chk.check_multiple_archs(files)
    print(f"[.] Building package '{package}' for arch '{arch}' from dpkg cache...")
    base_folder, control_folder = crt.create_deb_directory(package)
    output_folder = crt.create_output_dir()
    crt.copy_files(files, control_folder, base_folder)
    crt.create_control(package, control_folder, arch)
    crt.build_deb(package, base_folder, output_folder)


if __name__ == "__main__":
    main(sys.argv)