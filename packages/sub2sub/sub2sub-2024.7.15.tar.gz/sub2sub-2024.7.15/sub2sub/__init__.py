# get the version
from importlib.metadata import version
__version__ = version('omip')

from .dataloader import DataLoader