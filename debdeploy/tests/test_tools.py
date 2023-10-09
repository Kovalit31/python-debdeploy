'''

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

Test debdeploy.tools
'''

import os

from debdeploy import tools

def test_check_sudo() -> None:
    '''
    Tests check_sudo
    '''
    try:
        tools.check_sudo()
        assert os.getuid() == 0
    except PermissionError:
        assert os.getuid() != 0

def test_gen_uuid() -> None:
    '''
    Tests gen_uuid
    '''
    assert tools.gen_uuid() != tools.gen_uuid()
    assert len(tools.gen_uuid()) == 20
    assert len(tools.gen_uuid(30)) == 30

def test_normalize_re() -> None:
    '''
    Tests normalize_re
    '''
    assert tools.normalize_re(r"\d") == r"\d"
    assert tools.normalize_re(r"\\d+") == r"\\d\+"
