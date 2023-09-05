'''
Contains a control file parser
'''
import copy
import re

from debdeploy.tools import definitions

# pylint: disable=[too-few-public-methods]
class Package:
    '''
    Class, what defines package with it name, version, and, if defined, arch.
    Useful for defining package in any depend.
    '''
    def __init__(self, package, version=None, arch=None) -> None:
        self.package = package
        self.version = version
        self.arch = arch

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

def get_controls(package: Package) -> list[Control]:
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
        if x.strip().lower() == f"package: {package.package}":
            found = True
        if x.strip().lower() == "" and found:
            found = False
            _controls.append(copy.deepcopy(_control))
            _control = []
        if found:
            _control.append(x)
    if len(_controls) == 0:
        return None
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
        version = version[0].strip("()") if len(version) > 1 else None
        package, *arch = package.split(":", 1)
        return Package(package, version=version, arch=arch if len(arch) > 1 else None)
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
