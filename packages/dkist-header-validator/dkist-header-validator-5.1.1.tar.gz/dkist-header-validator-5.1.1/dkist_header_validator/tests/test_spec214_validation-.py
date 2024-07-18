from io import BytesIO
from pathlib import Path

import numpy as np
import pytest

from dkist_header_validator import spec214_l0_validator
from dkist_header_validator import spec214_validator
from dkist_header_validator import Spec214ValidationException
from dkist_header_validator.exceptions import ReturnTypeException
from dkist_header_validator.exceptions import ValidationException


def test_spec214l0_return_BytesIO_without_data(valid_spec_214l0_no_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: Raise return type exception
    """
    # raises exception on failure
    with pytest.raises(ReturnTypeException):
        result = spec214_l0_validator.validate(
            valid_spec_214l0_no_file, return_type=BytesIO, extra=False
        )
        assert isinstance(result, BytesIO)


def test_spec214_return_BytesIO_without_data(valid_spec_214_no_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: Raise return type exception
    """
    # raises exception on failure
    with pytest.raises(ReturnTypeException):
        result = spec214_validator.validate(
            valid_spec_214_no_file, return_type=BytesIO, extra=False
        )
        assert isinstance(result, BytesIO)


def test_spec214l0_return_file_without_data(valid_spec_214l0_no_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: raise a return type exception
    """
    # raises exception on failure
    with pytest.raises(ReturnTypeException):
        result = spec214_l0_validator.validate(
            valid_spec_214l0_no_file, return_type=Path, extra=False
        )
        assert isinstance(result, Path)


def test_spec214_return_file_without_data(valid_spec_214_no_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: raise a return type exception
    """
    # raises exception on failure
    with pytest.raises(ReturnTypeException):
        result = spec214_validator.validate(valid_spec_214_no_file, return_type=Path, extra=False)
        assert isinstance(result, Path)


def test_spec214l0_invalid_headers(invalid_spec_214l0_object):
    """
    Validates an invalid fits header against the SPEC-214 schema
    Given: A invalid SPEC-214 fits header
    When: Validating headers
    Then: raise a Spec214ValidationException
    """

    with pytest.raises(Spec214ValidationException):
        spec214_l0_validator.validate(invalid_spec_214l0_object)


def test_spec214_invalid_headers(invalid_spec_214_object):
    """
    Validates an invalid fits header against the SPEC-214 schema
    Given: A invalid SPEC-214 fits header
    When: Validating headers
    Then: raise a Spec214ValidationException
    """

    with pytest.raises(Spec214ValidationException):
        spec214_validator.validate(invalid_spec_214_object)


@pytest.mark.parametrize("instrument", ["cryo-nirsp", "dlnirsp", "vbi", "visp", "vtf"])
def test_spec214l0_instrument_required_key_missing(invalid_instrument_table_spec_214l0_object):
    """
    Given: Headers from a specific instrument, but with one of the required header keys removed
    When: Validating headers
    Then: The correct Error is raised
    """
    fits_object, missing_key = invalid_instrument_table_spec_214l0_object
    with pytest.raises(
        Spec214ValidationException, match=f"'{missing_key}': 'required key not provided"
    ):
        spec214_l0_validator.validate(fits_object)


@pytest.fixture(scope="module")
def invalid_file_params(tmpdir_factory):
    """
    Create a dict of invalid file params to be used in failing
    tests below.
    """
    temp_dir = tmpdir_factory.mktemp("invalid_file_params_temp")
    non_existent_file_name = temp_dir.join("tmp_fits_file.fits")
    non_fits_file_name = temp_dir.join("tmp_this_is_not_a_fits_file.dat")
    temp_array = np.ones(1, dtype=np.int16)
    temp_array.tofile(str(non_fits_file_name))
    yield {"file not found": non_existent_file_name, "file_not_fits": non_fits_file_name}


@pytest.fixture(scope="function", params=["file not found", "file_not_fits"])
def invalid_file_param(request, invalid_file_params):
    yield invalid_file_params[request.param]


def test_file_errors(invalid_file_param):
    """
    Validates an invalid file spec
    Given: A invalid file specification: non-existent file or non-fits file
    When: Validating headers
    Then: raise a Spec214ValidationException
    """

    with pytest.raises(ValidationException):
        spec214_l0_validator.validate(invalid_file_param)


def test_invalid_compressed_spec214l0(invalid_spec_214l0_compressed):
    """
    Validates an invalid compressed spec214 compliant file
    Given: An invalid compressed SPEC-0214 file
    When: Validating headers
    Then: Catch a warning and raise an exception
    """
    with pytest.raises(Spec214ValidationException):
        spec214_l0_validator.validate(invalid_spec_214l0_compressed)


def test_invalid_compressed_spec214(invalid_spec_214_compressed):
    """
    Validates an invalid compressed spec214 compliant file
    Given: An invalid compressed SPEC-0214 file
    When: Validating headers
    Then: Catch a warning and raise an exception
    """
    with pytest.raises(Spec214ValidationException):
        spec214_validator.validate(invalid_spec_214_compressed)


def test_validatel0_toomanyHDUs(valid_spec_214_l0_too_many_HDUs):
    """
    Validates headers with too many (more than 2) HDUs
    Given: A valid SPEC-214 file or HDUList with more than two headers
    When: Validating headers
    Then: Raise an exception
    """
    # raises exception on failure
    with pytest.raises(ValidationException):
        spec214_l0_validator.validate(valid_spec_214_l0_too_many_HDUs)


def test_validate_toomanyHDUs(valid_spec_214_too_many_HDUs):
    """
    Validates headers with too many (more than 2) HDUs
    Given: A valid SPEC-214 file or HDUList with more than two headers
    When: Validating headers
    Then: Raise an exception
    """
    # raises exception on failure
    with pytest.raises(ValidationException):
        spec214_validator.validate(valid_spec_214_too_many_HDUs)


def test_polarimetric_required_key_missing(invalid_polarimetric_spec_214_object):
    """
    Given: Polarimetric headers with a missing `polarimetric_required` key
    When: Validating headers
    Then: The correct Error is raised
    """
    with pytest.raises(
        Spec214ValidationException,
        match="'POL_SENS': 'required key not provided. Required keyword not present'",
    ):
        spec214_validator.validate(invalid_polarimetric_spec_214_object)


@pytest.mark.parametrize("instrument", ["cryo-nirsp", "dlnirsp", "vbi", "visp", "vtf"])
def test_instrument_required_key_missing(invalid_instrument_table_spec_214_object):
    """
    Given: Headers from a specific instrument, but with one of the required header keys removed
    When: Validating headers
    Then: The correct Error is raised
    """
    fits_object, missing_key = invalid_instrument_table_spec_214_object
    with pytest.raises(
        Spec214ValidationException, match=f"'{missing_key}': 'required key not provided"
    ):
        spec214_validator.validate(fits_object)
