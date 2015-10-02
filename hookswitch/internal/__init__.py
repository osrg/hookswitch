import sys
assert sys.version_info < (3, 0), 'Python 3k is not supported yet'

from . import common
LOG = common.init_logger()
