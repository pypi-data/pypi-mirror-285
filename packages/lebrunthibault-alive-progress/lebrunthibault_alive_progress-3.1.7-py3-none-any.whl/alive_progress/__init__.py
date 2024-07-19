from .core.configuration import config_handler
from .core.progress import alive_bar, alive_it

VERSION = (3, 1, 7)

__author__ = 'Thibault Lebrun'
__email__ = 'thibaultlebrun@live.fr'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'A new kind of Progress Bar, with real-time throughput, ' \
                  'ETA, and very cool animations!'

__all__ = ('alive_bar', 'alive_it', 'config_handler')
