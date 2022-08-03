import os
import shutil

def create_deb_directory(package, base_folder=os.path.join("/", "tmp")):
    '''
    Creating base folder of any deb package build tree and returns:
    1. Base folder
    2. Folder for control and dpkg processing files
    '''
    base_folder = os.path.join(base_folder, package)
    control_folder = os.path.join(base_folder, "DEBIAN")
    try:
        os.makedirs(control_folder)
    except:
        print(f"[*] Directory {base_folder} and {control_folder} already exists, skipping...")
    return base_folder, control_folder

def create_output_dir(base_folder=os.path.join("/", "tmp")):
    '''
    Creating dir, what to be contain builded packages
    '''
    debs_folder = os.path.join(base_folder, "DEBS")
    try:
        os.makedirs(debs_folder)
    except:
        print(f"[*] Directory {debs_folder} already exists, skipping...")
    return debs_folder

def copy_files(files, control_folder, base_folder):
    '''
    Copy dpkg processing files from 'files' list to 'control_folder' with postworking
    '''
    for x in files:
        output = x.split(".")[1]
        info_path = os.path.join("/", "var", "lib", "dpkg", "info")
        if not os.path.exists(info_path):
            raise OSError("\n[@] Your OS not Debian-based linux distribution.")
        full_input_path = os.path.join(info_path, x)
        full_output_path = os.path.join(control_folder, output)
        shutil.copy(full_input_path, full_output_path)
        if output.rstrip().endswith("rm") or output.rstrip().endswith("inst"):
            os.chmod(full_output_path, 0o755)
        if output.rstrip() == "list":
            with open(full_output_path) as f:
                for y in f.readlines():
                    if not y == ".":
                        y = y[:-len("\n")]
                        if os.path.isdir(y):
                            try:
                                os.makedirs(os.path.join(base_folder, y[1:]))
                            except:
                                pass
                        else:
                            try:
                                shutil.copyfile(y, os.path.join(base_folder, y[1:]))
                            except:
                                print("\n[WARNING] Distribution is not full. It may caaused by system damage.")
                f.close()
            os.remove(full_output_path)

def create_control(package: str, control_folder: str, arch: str):
    '''
    Create 'control' file for building package into 'control_folder'
    '''
    control_lines = []
    dependies = []
    with open(os.path.join("/", "var", "lib", "dpkg", "status")) as f:
        found = 0
        start = 1
        lines = f.readlines()
        for m in lines:
            x = m.lower()
            if not start:
                print(x)
                if found:
                    if x.startswith("\n") and x.endswith("\n"):
                        break
                    if x.startswith("status: "):
                        pass
                    elif x.startswith("depends: ") or x.startswith("pre-depends: "):
                        dependies = x.split(": ")[1][:-1].split(", ")
                        control_lines.append(m)
                    elif x.startswith("architecture: "):
                        control_lines.append(m)
                    else:
                        control_lines.append(m)
            else:
                if x == "package: {0}\n".format(package.lower()):
                    print("found")
                    control_lines = []
                    found = 1
                    start = 0
                    control_lines.append("Package: {0}\n".format(package))
                    continue
        print(dependies)
        print(control_lines)
        f.close()
    if len(control_lines) == 0:
        raise FileNotFoundError("\n[@] Package not found in status")
    with open(os.path.join(control_folder, "control"), "w") as f:
        f.write("".join(control_lines))
        f.close()

def build_deb(package, base_folder, debs_folder):
    '''
    Build DEB package into 'debs_folder'
    '''
    s = os.system(f"dpkg-deb -b -Sextreme {base_folder} {debs_folder}/{package}.deb")
    if s != 0:
        raise Exception("\n[@]You haven't installed 'dpkg-dev' package. Install it with 'apt'")