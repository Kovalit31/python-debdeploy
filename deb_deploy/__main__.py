import sys
import deb_deploy.tools.create as crt
import deb_deploy.tools.check as chk

def main(args):
    for x in args[1:]:
        version_have = False
        package, version, returned, arch = crt.get_data(x)
        if version == None:
            version = False
        else:
            version_have = True
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