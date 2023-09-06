'''
Tools module. Contains tools for extracting and work with package files
'''
import os

from . import control, definitions, files, build

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
        if level == "w" else "@" if level == "e" else "&" if not 'c' else '`'
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
