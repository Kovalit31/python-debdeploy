import sys
import deb_deploy.tools.create as crt
import deb_deploy.tools.check as chk

def main(args):
    builded = set()
    depends = set()
    for x in args[1:]:
        if x.startswith("-"):
            continue
        depends.add(x)

    while len(depends) > 0:
        lx = list(depends)
        lx.sort()
        x = lx[0]
        if x in builded:
            depends.remove(x)
            continue
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
        dependies = crt.create_control(package, control_folder, arch)
        crt.build_deb(package, base_folder, output_folder)
        print(lx, x, builded, depends, dependies)
        for x in range(len(dependies)):
            depends.add(dependies[x])
        builded.add(x)
        depends.discard(x)


if __name__ == "__main__":
    main(sys.argv)