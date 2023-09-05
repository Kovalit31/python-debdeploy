'''
Package builder
'''
import os

from debdeploy import tools
from debdeploy.tools import control, definitions

def build(package: control.Package, cache_dir: str, dest_dir: str) -> None:
    '''
    Builder of package
    '''
    if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
        tools.printf(f"Directory is not a directory: '{dest_dir}'!")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    tools.printf(f"Building package {package.package}:{package.arch} ({package.version})")
    _code = execute(
        f"sudo dpkg-deb -Sextreme -b {os.path.join(cache_dir, package.package)} \
            {os.path.join(dest_dir, f'{package.package}_{package.version}_{package.arch}.deb')}"
        )
    if _code == 0:
        return
    tools.printf("Error building package! Consider install dpkg-dev package!" if _code == 127
                 else "Build error!" ,
                 level='f',
                 exception=definitions.NotSupportedSystemError if _code == 127
                   else definitions.PackageBuildError)

def execute(cmd: str) -> int:
    '''
    Wrap around os.system()
    '''
    return os.system(cmd)
