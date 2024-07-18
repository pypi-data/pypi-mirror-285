"""Package providing support classes and methods used by all workflow tasks."""
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from dkist_header_validator.exceptions import *
from dkist_header_validator.spec_validators import *

try:
    __version__ = version(distribution_name=__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
