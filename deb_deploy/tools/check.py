import os
paths = {"info": os.path.join("/", "var", "lib", "dpkg", "info"), "dpkg": os.path.join("/", "var", "lib", "dpkg")}

def check_and_return_info_files(package):
    '''
    Returns configuration files, what is in "info" directory of dpkg
    '''
    archs = ["amd64", "i386", "arm64", "powerpc"]
    global paths
    info_files_path = paths["info"]
    if not os.path.exists(info_files_path):
        raise OSError("Your OS not Debian-based linux distribution")
    searched = []
    for x in archs:
        for y in os.listdir(info_files_path):
            if y.startswith(package + ":" + x + "."):
                searched.append(y)
    for x in os.listdir(info_files_path):
        if x.startswith(package + "."):
            searched.append(x)
    if len(searched) <= 0:
        raise Exception("Package not installed on this system")
    else:
        return searched

def check_multiple_archs(list_of_files):
    '''
    Checks for multiple archs of package and asks for and return needed arch
    Can be overrided later in "config.py".
    '''
    found_archs = []
    for x in list_of_files:
        s =  x.split(".")[0]
        if ":" in s:
            a = s.split(":")[1]
        else:
            a = "default"
        if not a in found_archs:
            found_archs.append(a)
    if len(found_archs) > 1:
        output = 0
        output_list = []
        output_str = "I'm found multiple archs of this package. What arch of package do you want to build?\n"
        for x in range(len(found_archs)):
            output_str += str(x) + ". " + found_archs[x] + "\n"
        output_str += "Please write a number of arch from under writed list: "
        while True:
            a = input(output_str)
            try:
                output = int(a)
                break
            except:
                print("You can type a number, please? Or you haven't got a keyboard?\n")
        for x in list_of_files:
            s = x.split(".")[0]
            if ":" in s:
                a = s.split(":")[1]
            else:
                a = "default"
            if found_archs[output] == a:
                output_list.append(x)
        return found_archs[output], output_list
    else:
        return found_archs[0], list_of_files

def check_perms():
    '''
    Checks for root permissions.
    '''
    if os.getuid() == 0:
        pass
    else:
        raise PermissionError("Access is denied: no root permissions")