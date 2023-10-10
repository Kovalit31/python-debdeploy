"""

    debdeploy - Build dpkg package and it dependencies from dpkg cache
    Copyright (C) 2023 Kovalit31

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

Definitions of module
"""

import os

DEBDEPLOY_CACHE_WORKDIR = "/tmp/debdeploy-{uuid}-cache"
DEBDEPLOY_WORKDIR = "/tmp/debdeploy-{uuid}"

DPKG_CACHE_LIB_ROOT = os.path.join("/", "var", "lib", "dpkg")
DPKG_CACHE_STATUS = os.path.join(DPKG_CACHE_LIB_ROOT, "status")
DPKG_CACHE_INFO_FILES_ROOT = os.path.join(DPKG_CACHE_LIB_ROOT, "info")

CONTROL_SECTION_REGEX = "^[^\n]+:( [^\n]+)?$"
PACKAGE_INFO_FILE_REGEX = "^{package}(:[a-z0-9]+)?\\.[a-z]+$"

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


class PlatformNotSupportedError(Exception):
    pass


# pylint: enable=[missing-class-docstring]
