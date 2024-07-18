"""
Test for the base validator
"""
from pathlib import Path

import numpy as np
import pytest
import voluptuous as vol
import yaml
from astropy.io import fits
from deepdiff import DeepDiff

from dkist_header_validator.base_validator import SpecSchema
from dkist_header_validator.base_validator import SpecValidator
from dkist_header_validator.exceptions import SpecSchemaDefinitionException
from dkist_header_validator.exceptions import SpecValidationException
from dkist_header_validator.exceptions import ValidationException


def test_parse_spec_schema_definitions():
    """
    Given: A valid schema definition, can be in one of the following formats:
        dict[str, dict[str, Any]]
    When: Validating the schema
    Then: SpecSchema(definition) returns the schema definition in dict form
    """
    example_schema = {
        "fits": {
            "key_004": {
                "expand": True,
                "required": False,
                "comment": "comment 4",
                "type": "bool",
            }
        }
    }
    SpecSchema._parse_spec_schema_definitions(example_schema)


@pytest.fixture(scope="module")
def invalid_definition_format_params(tmpdir_factory):
    """
    Create a dict of invalid schema definition formats to be used in
    failing format tests below.
    """
    invalid_dict = {"specxxx": {"this is not a valid yaml file"}}

    temp_dir = tmpdir_factory.mktemp("invalid_definitions_temp")
    file_name = temp_dir.join("invalid_yaml_file.yml")
    file_name.write(yaml.safe_dump_all(invalid_dict))

    test_params = {
        "invalid Dict": dict(),
        "invalid schema type1": "non valid schema type",
    }

    yield test_params


@pytest.fixture(
    scope="function",
    params=[
        "invalid Dict",
        "invalid schema type1",
    ],
)
def invalid_definition_format(request, invalid_definition_format_params):
    yield invalid_definition_format_params[request.param]


def test_parse_spec_schema_definitions_fail(invalid_definition_format):
    """
    Given: A schema definition that is empty or not in one of the valid formats:
        List[dict]
    When: Validating the schema
    Then: raises a SpecSchemaDefinitionException
    """
    with pytest.raises(SpecSchemaDefinitionException):
        SpecSchema._parse_spec_schema_definitions(invalid_definition_format)


@pytest.fixture(scope="module")
def valid_schema_definition_params():
    """
    Create a dict of schema definition parameters that spans the valid
    parameter space. To be used in successful schema definition tests below.
    """

    test_params = {
        "required int": {"fits": {"keyword_name": {"required": True, "type": "int"}}},
        "optional int": {"fits": {"keyword_name": {"required": False, "type": "int"}}},
        "required float": {"fits": {"keyword_name": {"required": True, "type": "float"}}},
        "optional float": {"fits": {"keyword_name": {"required": False, "type": "float"}}},
        "required str": {"fits": {"keyword_name": {"required": True, "type": "str"}}},
        "optional str": {"fits": {"keyword_name": {"required": False, "type": "str"}}},
        "required bool": {"fits": {"keyword_name": {"required": True, "type": "bool"}}},
        "optional bool": {"fits": {"keyword_name": {"required": False, "type": "bool"}}},
        "optional key-value pair 1": {
            "fits": {"keyword_name": {"required": True, "type": "int", "optional1": "value1"}}
        },
        "optional key-value pair 2": {
            "fits": {"keyword_name": {"required": False, "type": "int", "optional2": "value2"}}
        },
        "optional key-value pair 3": {
            "fits": {"keyword_name": {"required": True, "type": "float", "optional3": "value3"}}
        },
        "optional key-value pair 4": {
            "fits": {"keyword_name": {"required": False, "type": "float", "optional4": "value4"}}
        },
        "optional key-value pair 5": {
            "fits": {"keyword_name": {"required": True, "type": "str", "optional5": "value5"}}
        },
        "optional key-value pair 6": {
            "fits": {"keyword_name": {"required": False, "type": "str", "optional6": "value6"}}
        },
        "optional key-value pair 7": {
            "fits": {"keyword_name": {"required": True, "type": "bool", "optional7": "value7"}}
        },
        "optional key-value pair 8": {
            "fits": {"keyword_name": {"required": False, "type": "bool", "optional8": "value8"}}
        },
    }

    return test_params


@pytest.fixture(
    scope="function",
    params=[
        "required int",
        "optional int",
        "required float",
        "optional float",
        "required str",
        "optional str",
        "required bool",
        "optional bool",
        "optional key-value pair 1",
        "optional key-value pair 2",
        "optional key-value pair 3",
        "optional key-value pair 4",
        "optional key-value pair 5",
        "optional key-value pair 6",
        "optional key-value pair 7",
        "optional key-value pair 8",
    ],
)
def valid_schema_definition(request, valid_schema_definition_params):

    yield valid_schema_definition_params[request.param]


def test_validate_spec_schema_definitions(valid_schema_definition):
    """
    Given: Valid schema definitions that span the parameter space of the definition schema
    When: Validating the schema
    Then: SpecSchema(definition) successfully validates the definition against
        the definition schema. Success means no exception is raised.
    """
    SpecSchema(valid_schema_definition)


@pytest.fixture(scope="module")
def invalid_schema_definition_params():
    """
    Create a dict of invalid schema definition parameters to be used in
    failing tests below.
    """

    test_params = {
        "missing required": {"specxxx": {"keyword": {"type": "int"}}},
        "missing type": {"specxxx": {"keyword": {"required": True}}},
        "missing both, no optional": {"specxxx": {"keyword": {}}},
        "missing both, with optional": {"specxxx": {"keyword": {"optional": "value"}}},
    }

    yield test_params


@pytest.fixture(
    scope="function",
    params=[
        "missing required",
        "missing type",
        "missing both, no optional",
        "missing both, with optional",
    ],
)
def invalid_schema_definition(request, invalid_schema_definition_params):

    yield invalid_schema_definition_params[request.param]


def test_validate_spec_schema_definitions_fail(invalid_schema_definition):
    """
    Given: Schema definitions that do not meet the definition schema
    When: Validating the schema
    Then: SpecSchema(definition) raises a SpecSchemaDefinitionException
    """
    with pytest.raises(SpecSchemaDefinitionException):
        SpecSchema(invalid_schema_definition)


@pytest.fixture(scope="module")
def valid_values_list_params():
    """
    Create a dict of valid values lists to be used in successful tests below
    """
    test_params = {
        "str list": ["a", "b", "c"],
        "int list": [1, 2, 3],
        "float list": [1.0, 2.0, 3.0],
        "bool list": [True, False, False, True],
        "mixed list": ["a", 1, 2.0, True],
    }

    yield test_params


@pytest.fixture(
    scope="function", params=["str list", "int list", "float list", "bool list", "mixed list"]
)
def valid_values_list(request, valid_values_list_params):
    yield valid_values_list_params[request.param]


def test_validate_spec_schema_definitions_values_list(valid_values_list):
    """
    Given: Schema definitions that have valid values lists
    When: Validating the schema
    Then: SpecSchema(definition) does not raise a SpecSchemaDefinitionException
    """
    test_schema = {
        "fits": {"keyword_name": {"required": True, "type": "int", "values": valid_values_list}}
    }
    SpecSchema(test_schema)


@pytest.fixture(scope="module")
def invalid_values_list_params():
    """
    Create a dict of invalid values 'lists' to be used in failing tests below
    """
    test_params = {
        "non-list (set)": {"a", 1, 2.0, True},
        "non-list (tuple)": ("a", 1, 2.0, True),
        "non-list (scalar)": 1,
        "non-list (string)": "some string",
    }

    yield test_params


@pytest.fixture(
    scope="function",
    params=["non-list (set)", "non-list (tuple)", "non-list (scalar)", "non-list (string)"],
)
def invalid_values_list(request, invalid_values_list_params):
    yield invalid_values_list_params[request.param]


def test_validate_spec_schema_definitions_values_list_fail(invalid_values_list):
    """
    Given: Schema definitions that have invalid values lists
    When: Validating the schema
    Then: SpecSchema(definition) raises a SpecSchemaDefinitionException
    """
    test_schema = {
        "fits": {
            "keyword_name": {
                "required": True,
                "type": "int",
                "values": invalid_values_list,
            }
        }
    }

    with pytest.raises(SpecSchemaDefinitionException):
        SpecSchema(test_schema)


@pytest.fixture(scope="module")
def define_test_schema_definition():
    """
    Create a test schema to be used tested against in both successful and failing
    tests below.
    """
    test_schema_definition = {
        "fits": {
            "key_001": {
                "expand": False,
                "required": False,
                "comment": "comment 1",
                "type": "float",
            },
            "key_002": {
                "expand": False,
                "required": True,
                "comment": "comment 2",
                "type": "str",
            },
            "key_003": {
                "expand": False,
                "required": True,
                "comment": "comment 3",
                "type": "int",
            },
            "key_004": {
                "expand": False,
                "required": False,
                "comment": "comment 4",
                "type": "bool",
            },
        }
    }

    yield test_schema_definition


def test_create_spec_schema(define_test_schema_definition):
    """
    Given: A valid schema definition and a valid test schema for the definition
    When: Creating the schema
    Then: The valid test schema is successfully parsed by the schema definition
    """
    schema = SpecSchema(define_test_schema_definition)

    input_dict = {"key_002": "value_002", "key_003": 314159, "key_001": 3.14159}

    assert not DeepDiff(input_dict, schema(input_dict, extra=True), ignore_order=True)


def test_create_spec_schema_fail(define_test_schema_definition):
    """
    Given: A valid schema definition and an invalid test schema for the definition
    When: Creating the schema
    Then: The invalid test schema is not successfully parsed by the schema definition
        and a voluptuous exception is raised.
    """
    schema = SpecSchema(define_test_schema_definition)

    # Required key key_003 is missing:
    input_dict = {"fits": {"key_002": "value_002", "key_004": False, "key_001": 3.14159}}
    with pytest.raises(vol.MultipleInvalid):
        schema(input_dict, extra=True)


@pytest.fixture(scope="module")
def spec_validator():
    """
    Create a schema validator to test fits headers against below.
    """
    test_schema = {
        "fits": {
            "BITPIX": {
                "expand": False,
                "required": True,
                "type": "int",
                "values": [8, 16, 32, 64, -32, -64],
            },
            "NAXIS": {"expand": True, "required": True, "type": "int", "values": [3]},
            "NAXIS1": {"expand": False, "required": True, "type": "int"},
            "NAXIS2": {"expand": False, "required": True, "type": "int"},
            "NAXIS3": {"expand": False, "required": True, "type": "int", "default_value": 1},
        }
    }

    spec_schema = SpecSchema(test_schema)
    spec_validator = SpecValidator(spec_schema)

    yield spec_validator


@pytest.fixture(scope="module")
def valid_test_header_params(tmpdir_factory):
    """
    Create a dict with a valid header in various formats to be successfully tested
    against the schema defined above
    """
    temp_dir = tmpdir_factory.mktemp("valid test_headers_temp")
    file_name = temp_dir.join("tmp_fits_file.fits")
    valid_array = np.ones((1, 1, 1), dtype=float)
    valid_hdu = fits.PrimaryHDU(valid_array)
    valid_hdu_list = fits.HDUList([valid_hdu])
    valid_hdu_list.writeto(str(file_name))

    yield {
        "valid_hdu_list": valid_hdu_list,
        "valid_fits_header": valid_hdu_list[0].header,
        "valid_fits_file": Path(file_name),
    }


@pytest.fixture(
    scope="function",
    params=["valid_hdu_list", "valid_fits_header", "valid_fits_file"],
)
def valid_test_header(request, valid_test_header_params):
    yield valid_test_header_params[request.param]


def test_spec_validator(spec_validator, valid_test_header):
    """
    Given: A valid schema and a valid fits header to test against the schema
    When: Header validation
    Then: SpecValidator successfully validates the header and does not raise an exception
    """
    spec_validator.validate(valid_test_header)


@pytest.fixture(scope="module")
def valid_test_compressed_file(tmpdir_factory):
    """
    Create a compressed file with a valid header in various formats to be successfully tested
    against the schema defined above
    """
    temp_dir = tmpdir_factory.mktemp("valid test_headers_temp")
    file_name = temp_dir.join("tmp_fits_file.fits")
    valid_array = np.ones((1, 1, 1), dtype=float)
    primary_hdu = fits.PrimaryHDU()
    valid_hdu = fits.CompImageHDU(valid_array)
    valid_hdu_list = fits.HDUList([primary_hdu, valid_hdu])
    valid_hdu_list.writeto(str(file_name))

    yield {
        "valid_compressed.fits.fz": Path(file_name),
    }


@pytest.fixture(
    scope="function",
    params=["valid_compressed.fits.fz"],
)
def valid_test_compressed_files(request, valid_test_compressed_file):
    yield valid_test_compressed_file[request.param]


def test_spec_validator_file(spec_validator, valid_test_compressed_files):
    """
    Given: A valid schema and a valid compressed fits file to test against the schema
    When: Header validation
    Then: SpecValidator successfully validates the header and does not raise an exception
    """
    spec_validator.validate(valid_test_compressed_files)


@pytest.fixture(scope="module")
def invalid_test_header_params(tmpdir_factory):
    """
    Create a dict with an invalid header to be tested against the schema defined above.
    The header is invalid because the schema requires NAXIS to be 3 and here we create
    a 2D array which means NAXIS=2.
    """
    temp_dir = tmpdir_factory.mktemp("invalid_test_headers_temp")
    file_name = temp_dir.join("tmp_fits_file.fits")
    invalid_array = np.ones((1, 1), dtype=float)
    primary_hdu = fits.PrimaryHDU()
    invalid_hdu = fits.CompImageHDU(invalid_array)
    invalid_hdu_list = fits.HDUList([primary_hdu, invalid_hdu])
    invalid_hdu_list.writeto(str(file_name))

    yield {
        "invalid_hdu_list": invalid_hdu_list,
        "invalid_fits_header": invalid_hdu_list[0].header,
        "invalid_fits_file": Path(file_name),
    }


@pytest.fixture(scope="function", params=["invalid_hdu_list", "invalid_fits_file"])
def invalid_test_header(request, invalid_test_header_params):
    yield invalid_test_header_params[request.param]


def test_spec_validator_fail(spec_validator, invalid_test_header):
    """
    Given: A valid schema and an invalid fits header to test against the schema
    When: Header validation
    Then: SpecValidator raises a SpecValidationException
    """
    with pytest.raises(SpecValidationException):
        spec_validator.validate(invalid_test_header)


def test_validation_exception():
    """
    Test ValidationException string format
    Given: a ValidationException class
    When: instance created with message and errors
    Then: String of ValidationException is as expected
    """
    message = "test message"
    errors = {"error1": "error text"}
    s = ValidationException(message, errors=errors)
    assert str(s) == f"{message}: errors={errors}"
