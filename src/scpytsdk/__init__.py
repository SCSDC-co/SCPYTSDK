from importlib.metadata import version

from scpytsdk._client import SCPYTSDK
from scpytsdk.enums import *
from scpytsdk.models import *

__version__ = version("scpytsdk")

__all__ = ["SCPYTSDK", "models", "enums"]
