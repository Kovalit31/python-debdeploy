'''
Root module of debeploy
Imports tools
'''

from . import tools
from . import __main__

def main() -> None:
    '''
    Main runner
    '''
    __main__.main(__main__.parse())
