"""
Common Exceptions for the fits-validator
"""


__all__ = [
    "ValidationException",
    "SpecSchemaDefinitionException",
    "SpecValidationException",
    "ReturnTypeException",
]


class ValidationException(Exception):
    """
    Base Exception for the validator
    """

    def __init__(self, message: str = "Errors during validation", errors: dict = None):
        self.message = message
        self.errors = errors

    def __str__(self):
        return f"{self.message}: errors={self.errors}"


class SpecSchemaDefinitionException(ValidationException):
    """
    Exception when validating the YAML Schemas
    """


class SpecValidationException(ValidationException):
    """
    Default spec validation exception
    """


class TranslationException(ValidationException):
    """
    Exception when translating
    """


class ReturnTypeException(Exception):
    """
    Exception when returning a BytesIO object
    """

    def __init__(self, message: str = "Return type error"):
        self.message = message
