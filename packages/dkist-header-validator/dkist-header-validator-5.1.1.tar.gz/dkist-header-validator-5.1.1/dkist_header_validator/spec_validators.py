"""
Validators configured for specific Fits Specs
"""
from dkist_fits_specifications.spec122 import load_processed_spec122
from dkist_fits_specifications.spec214 import load_processed_spec214
from dkist_fits_specifications.spec214.level0 import load_level0_spec214

from dkist_header_validator.base_validator import ProcessedSpecValidator
from dkist_header_validator.exceptions import SpecValidationException

__all__ = [
    "spec122_validator",
    "Spec122ValidationException",
    "spec214_validator",
    "spec214_l0_validator",
    "Spec214ValidationException",
]


############
# SPEC-122 #
############


class Spec122ValidationException(SpecValidationException):
    """
    Exception when validating a spec 122 file
    """


spec122_validator = ProcessedSpecValidator(
    spec_processor_function=load_processed_spec122,
    SchemaValidationException=Spec122ValidationException,
)


############
# SPEC-214 #
############
class Spec214ValidationException(SpecValidationException):
    """
    Exception when validating a spec 214 file
    """


spec214_l0_validator = ProcessedSpecValidator(
    spec_processor_function=load_level0_spec214,
    SchemaValidationException=Spec214ValidationException,
)

spec214_validator = ProcessedSpecValidator(
    spec_processor_function=load_processed_spec214,
    SchemaValidationException=Spec214ValidationException,
)
