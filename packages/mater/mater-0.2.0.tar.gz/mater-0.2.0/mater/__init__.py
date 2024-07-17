from .core.model import Mater
from importlib.metadata import version

Mater.__version__ = version("mater")  # to have the __version__ of the mater package
