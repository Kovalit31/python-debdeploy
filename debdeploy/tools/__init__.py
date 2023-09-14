'''
Tools module. Contains tools for extracting and work with package files
'''
import os
import platform
import re

from . import control, definitions, files, build, version

def check_sudo() -> bool:
    '''
    Checks for sudo permission
    If there isn't root, return False
    '''
    return os.getuid() == 0

def printf(*message, level="i", exception=Exception, check=False):
    '''
    Print meassage with small styling
    '''
    if check:
        return
    level = level[0].lower()
    symbol = "#" if level == 'd' else "~" if level == 'v' else '*' if level == "i" else "!" \
        if level == "w" else "@" if level == "e" else "&" if level != 'c' else '`'
    out_msg = f"[{symbol}] {''.join(message)}"
    print(
        out_msg
    )
    if level == "f":
        # pylint: disable=[broad-exception-raised]
        raise exception(out_msg)

def force_makedirs(path: str, mode=None) -> None:
    '''
    Forces making of directory @string path
    '''
    if os.path.isfile(path):
        printf(f"Can't create dircetory, if it is file: '{path}'!", level='e')
        return
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            pass
    if mode is None:
        return
    os.chmod(path, mode)

def get_arch() -> str:
    '''
    Gets arch of host machine
    '''
    # pylint: disable=[implicit-str-concat]
    _a_re = ["i.86/i386", "x86_64/amd64", "s390x/s390x", "aarch64.*/arm64"] # Predefined
    arch = platform.machine()
    for _x in _a_re:
        pattern, repl = _x.split("/")
        arch = re.sub(pattern, repl, arch)
    return arch
