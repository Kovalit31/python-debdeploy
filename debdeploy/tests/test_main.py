'''
Main programm tester
'''

import random

from argparse import Namespace

from .. import main, gen_uuid
from .. import tools

packeges = [
    "apt",
    "dpkg",
    "libc6",
    "tar"
]

def create_namespace(*_, **kwargs):
    '''
    Creates Namespace object to pass
    it as a string
    '''
    return Namespace(**kwargs)

def random_choose_package():
    '''
    Randomly chooses packages to build :)
    '''
    return random.choice(packeges)


def test_simple():
    '''
    Test avoiding build dependencies
    '''
    uuid = gen_uuid()
    destination = tools.definitions.DEBDEPLOY_WORKDIR.format(
        uuid=uuid
    )
    cache = tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(
        uuid=uuid
    )
    main(create_namespace(
        no_superuser = True,
        destination = destination,
        cache = cache,
        packages = [random_choose_package()],
        debug=False,
        dependencies=False
    ))

def test_depends():
    '''
    Test using build dependencies
    '''
    uuid = gen_uuid()
    destination = tools.definitions.DEBDEPLOY_WORKDIR.format(
        uuid=uuid
    )
    cache = tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(
        uuid=uuid
    )
    main(create_namespace(
        no_superuser = True,
        destination = destination,
        cache = cache,
        packages = [random_choose_package()],
        debug=False,
        dependencies=True
    ))

def test_simple_lots():
    '''
    Test without dependencies with many packages
    '''
    uuid = gen_uuid()
    destination = tools.definitions.DEBDEPLOY_WORKDIR.format(
        uuid=uuid
    )
    cache = tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(
        uuid=uuid
    )
    main(create_namespace(
        no_superuser = True,
        destination = destination,
        cache = cache,
        packages = packeges,
        debug=False,
        dependencies=False
    ))

def test_dependends_lot():
    '''
    Test with many packages with dependencies 
    '''
    uuid = gen_uuid()
    destination = tools.definitions.DEBDEPLOY_WORKDIR.format(
        uuid=uuid
    )
    cache = tools.definitions.DEBDEPLOY_CACHE_WORKDIR.format(
        uuid=uuid
    )
    main(create_namespace(
        no_superuser = True,
        destination = destination,
        cache = cache,
        packages = packeges,
        debug=False,
        dependencies=True
    ))
