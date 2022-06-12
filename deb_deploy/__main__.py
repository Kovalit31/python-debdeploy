import os
import sys
import shutil
import deb_deploy.tools.create as crt
import deb_deploy.tools.check as chk

def main(args):
    if len(args) <= 1:
        pass
    else:
        print("Building package {0}".format(args[1].lstrip().rstrip().split(" ")[0]))
        if os.getuid() == 0:
            print("Sudo is granted, continuing...")
            path_dpkg = os.path.join("/", "var", "lib", "dpkg")
            if os.path.exists(path_dpkg):
                info_dpkg = os.path.join(path_dpkg, "info")
                tmp = os.path.join("/", "tmp", args[1].lstrip().rstrip().split(" ")[0])
                DEBIAN = os.path.join(tmp, "DEBIAN")
                try:
                    os.makedirs(DEBIAN)
                except:
                    pass
                if os.path.exists(info_dpkg):
                    sorted = []
                    #print(os.listdir(info_dpkg))
                    for x in os.listdir(info_dpkg):
                        if x.startswith(args[1].lstrip().rstrip().split(" ")[0]+":amd64"):
                            sorted.append(x)
                            print(x)
                            print(args[1].lstrip().rstrip().split(" ")[0]+":amd64")
                        elif x.startswith(args[1].lstrip().rstrip().split(" ")[0]+":i386"):
                            sorted.append(x)
                            print(x)
                            print(args[1].lstrip().rstrip().split(" ")[0]+":i386")
                        elif x.startswith(args[1].lstrip().rstrip().split(" ")[0]):
                            sorted.append(x)
                            print(x)
                            print(args[1].lstrip().rstrip().split(" ")[0])
                        else:
                            pass
                    print(sorted)
                    if len(sorted) > 0:
                        for x in sorted:
                            shutil.copyfile(os.path.join(info_dpkg, x), os.path.join(DEBIAN, x))
                            c =  x.split(".")[1]
                            if x.endswith(".list"):
                                with open(os.path.join(DEBIAN, x)) as f:
                                    for y in f.readlines():
                                        if not y == ".":
                                            y = y[:-len("\n")]
                                            if os.path.isdir(y):
                                                try:
                                                    os.makedirs(os.path.join(tmp, y[1:]))
                                                except:
                                                    pass
                                            else:
                                                try:
                                                    shutil.copyfile(y, os.path.join(tmp, y[1:]))
                                                except:
                                                    print("[WARNING] Distribution is not full. It may caaused by system damage.")
                                    f.close()
                                os.remove(os.path.join(DEBIAN, x))
                            else:
                                os.rename(os.path.join(DEBIAN, x), os.path.join(DEBIAN, c))
                        control_lines = []
                        dependies = []
                        with open(os.path.join(path_dpkg, "status")) as f:
                            found = 0
                            for x in f.readlines():
                                if x == "Package: {0}\n".format(args[1].lstrip().rstrip().split(" ")[0]):
                                    print("found")
                                    found = 1
                                if found:
                                    if x == "\n":
                                        break
                                    if x.startswith("Status: "):
                                        pass
                                    elif x.startswith("Depends: "):
                                        dependies = x.split(": ")[1][:-1].split(", ")
                                        control_lines.append(x)
                                    else:
                                        control_lines.append(x)
                            print(dependies)
                            print(control_lines)
                            f.close()
                        with open(os.path.join(DEBIAN, "control"), "w") as f:
                            f.write("".join(control_lines))
                            f.close()
                        debian_c = os.listdir(DEBIAN)
                        scripts = []
                        for x in debian_c:
                            if x.endswith("rm") or x.endswith("inst"):
                                scripts.append(x)
                        for x in scripts:
                            os.chmod(os.path.join(DEBIAN, x), 0o755)
                        print("building package...")
                        deb_path = os.path.join("/", "tmp", "debs")
                        try:
                            os.makedirs(deb_path)
                        except:
                            pass
                        print(f"# running dpkg-deb -b -Sextreme {tmp} {deb_path}/{os.path.basename(tmp)}.deb")
                        os.system(f"dpkg-deb -b -Sextreme {tmp} {deb_path}/{os.path.basename(tmp)}.deb")
                        return dependies
                    else:
                        raise Exception("No installed package on this system.\nAbort.")
            else:
                raise OSError("Your os not debian-based gnu/linux")
                    
        else:
            raise PermissionError("No admin right!")

# if __name__ == "__main__":
#     p = main(sys.argv)
#     dep_dep = []
#     try:
#         while True:
#             if len(p) > 0:
#                 print("Ready to build:", p, f"\nTotal {len(p)} pkgs\n", end=" ")
#                 print("Did you want to build dependencies?[Y/n]", end=" ")
#                 a = input()
#                 if a.lower() == "y" or a.lower() == "yes":
#                     for x in p:
#                         try:
#                             dep_dep.append(main(["", x]))
#                         except:
#                             print("##Failed to build {0}".format(x.lstrip().rstrip().split(" ")[0]))
#                     new = []
#                     for x in dep_dep:
#                         for y in x:
#                             if not y in new:
#                                 new.append(y)
#                     p = new
#                 else:
#                     print("Good luck!")
#                     break
#     except:
#         pass

def new_main(args):
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
    crt.build_deb(package, base_folder, output_folder)


if __name__ == "__main__":
    new_main(sys.argv)