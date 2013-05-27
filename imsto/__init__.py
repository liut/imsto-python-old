from _base import *
from _config import *
from _util import *
from image import *
from store import *

#__all__ = (_base.__all__ + _config.__all__ + _util.__all__)


VERSION = (1, 2, 1)


def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    return '.'.join(map(str, VERSION))

__version__ = get_version()
__author__ = 'Eagle Liut'
__author_email__ = 'liutao@liut.cc'
