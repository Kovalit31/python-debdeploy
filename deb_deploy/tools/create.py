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
            pass

def create_control(package, control_folder, arch):
    '''
    Create 'control' file for building package into 'control_folder'
    '''
    pass

def build_deb(package, base_folder, debs_folder):
    '''
    Build DEB package into 'debs_folder'
    '''
    s = os.system("echo 'OK'")
    if s != 0:
        raise Exception("\n[@]You haven't installed 'dpkg-dev' package. Install it with 'apt'")