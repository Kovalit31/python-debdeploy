'''
Contains a control file parser
'''
import copy
import re
from debdeploy.tools.version import LooseVersion

from debdeploy.tools import definitions
from debdeploy import tools

# pylint: disable=[too-few-public-methods]
class Package:
    '''
    Class, what defines package with it name, version, and, if defined, arch.
    Useful for defining package in any depend.
    '''
    def __init__(self, name: str, version=None, arch=None, modifier=None) -> None:
        self.name = name
        self.version = LooseVersion(vstring=version)
        self.arch = arch
        self.modifier = modifier

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Package):
            return False
        isversion = __value.version == self.version
        if __value.version is None:
            # Difficult question. I think it is True
            isversion = True
        isarch = __value.arch == self.arch
        if __value.arch is None:
            isarch = True
        # Name can't be None
        return __value.name == self.name and \
                isarch and \
                isversion

    def check_version(self, package, no_panic_return: bool = False) -> None:
        '''
        Check if package can be dependency.
        This package contains modifier, given package contains version
        If in given package have modifier, it will ignored
        If this package haven't got modifier, raise exception NoPackageModifierError
        '''
        if self.modifier is None:
            tools.printf(
                "This package doesn't contain modyfier or version, \
Can't check package compatibility!",
                level='f',
                exception=definitions.NoPackageModifierError,
                check=no_panic_return
                )
            return
        if not isinstance(package, Package):
            tools.printf(
                f"Can't use '{package}' as Package object!",
                level="f",
                exception=TypeError,
                check=no_panic_return
            )
            return
        if package.version is None:
            tools.printf(
                f"Can't determine version of '{package}'!",
                level='f',
                exception=ValueError,
                check=no_panic_return
            )
            return
        if package.name != self.name:
            return False
        if (package.arch is not None and self.arch is not None) and (package.arch != self.arch):
            return False
        return package.version == self.version if self.modifier == "=" \
            else package.version < self.version if self.modifier == "<<" \
                else package.version > self.version if self.modifier == ">>" \
                    else package.version >= self.version if self.modifier == ">=" \
                        else package.version <= self.version if self.modifier == "<=" \
                            else (tools.printf(
                                "Can't determine modifier!",
                                level='f',
                                exception=ValueError,
                                check=no_panic_return
                            ) or False)

class Control:
    '''
    Main control file parser
    '''
    def __init__(self, control: list[str]) -> None:
        '''
        Initializes instance and parses control
        '''
        self.sections = {}
        self.original = []
        latest = ""
        for line in control:
            if re.match(definitions.CONTROL_SECTION_REGEX, line.strip()):
                section, data = line.lower().strip().split(":", 1)
                latest = section
                self.sections[section] = data.strip()
            else:
                if latest != "":
                    self.sections[latest] = f"{self.sections[latest]}\n{line.strip()}".strip()
            if latest != "status":
                self.original.append(line)
        self.pre_depends_list = None
        self.depends_list = None
        self.recommends_list = None
        # Should never broke, because it is default package sections
        self.version = self.sections["version"]
        self.arch = self.sections["architecture"]
        self.package = self.sections["package"]

    def pre_depends(self) -> list[Package]:
        '''
        Returns copy of packages, in what pre-depends package
        '''
        if self.pre_depends_list is None:
            try:
                self.pre_depends_list = parse_packages(self.sections["pre-depends"])
            except KeyError:
                self.pre_depends_list = []
        return self.pre_depends_list

    def depends(self) -> list[Package]:
        '''
        Returns copy of packages, in what depends package
        '''
        if self.depends_list is None:
            try:
                self.depends_list = parse_packages(self.sections["depends"])
            except KeyError:
                self.depends_list = []
        return self.depends_list

    def recommends(self) -> list[Package]:
        '''
        Returns copy of packages, what recommends to be installed per package
        '''
        if self.recommends_list is None:
            try:
                self.recommends_list = parse_packages(self.sections["recommends"])
            except KeyError:
                self.recommends_list = []
        return self.recommends_list

    def debug__(self) -> str:
        '''
        Returns str with debug data
        '''
        return self.original

def get_controls(package_name: str) -> list[Control]:
    '''
    Finds control for package in status dpkg file
    '''
    _control = []
    # pylint: disable=[invalid-name] # Need to ignore non snake case
    with open(definitions.DPKG_CACHE_STATUS, encoding="utf-8") as f:
        status = f.readlines()
    found = False
    _controls = []
    # pylint: disable=[invalid-name]
    for x in status:
        if x.strip().lower() == f"package: {package_name}":
            found = True
        if x.strip().lower() == "" and found:
            found = False
            _controls.append(copy.deepcopy(_control))
            _control = []
        if found:
            _control.append(x)
    return [Control(x) for x in _controls]

def parse_packages(line: str) -> list[Package, list[Package]]:
    '''
    Parses line of packages into readable list of Package classes
    '''
    def generate_package(all_data: str) -> Package:
        '''
        Generates packages from package:arch (version)
        '''
        package, *version = all_data.split(" ", 1)
        modifier, *version = version[0].strip("()").split(" ", 1) if len(version) > 0 else (None,)
        package, *arch = package.split(":", 1)
        return Package(package,
                       version=version[0] if len(version) > 0 else None,
                       arch=arch[0] if len(arch) > 0 else None,
                       modifier=modifier)
    raw = line.split(",")
    out = []
    for package in raw:
        group = package.strip().split("|")
        if len(group) == 1:
            group = generate_package(group[0])
        else:
            group = [generate_package(x.strip()) for x in group]
        out.append(group)
    return out
