'''
Definitions of module
'''

import os

DPKG_CACHE_LIB_ROOT = os.path.join("/", "var", "lib", "dpkg")
DPKG_CACHE_STATUS = os.path.join(DPKG_CACHE_LIB_ROOT, "status")
DPKG_CACHE_INFO_FILES_ROOT = os.path.join(DPKG_CACHE_LIB_ROOT, "info")

CONTROL_SECTION_REGEX = "^[^\n]+:( [^\n]+)?$"
PACKAGE_INFO_FILE_REGEX = "^{package}(:[a-z]+)?\\.[a-z]+$"

SCRIPTS = "^(post|pre)(rm|inst)$"

# ===============
#   Exceptions
# ===============

# pylint: disable=[missing-class-docstring]
class PackageNotFoundError(Exception):
    pass

class NotSupportedSystemError(Exception):
    pass

class PackageBuildError(Exception):
    pass

class NoPackageModifierError(Exception):
    pass

# pylint: enable=[missing-class-docstring]
