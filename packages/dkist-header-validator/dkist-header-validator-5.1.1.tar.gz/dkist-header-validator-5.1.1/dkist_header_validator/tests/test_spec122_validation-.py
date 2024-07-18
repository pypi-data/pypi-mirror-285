from io import BytesIO
from pathlib import Path

import numpy as np
import pytest

from dkist_header_validator import spec122_validator
from dkist_header_validator import Spec122ValidationException
from dkist_header_validator.exceptions import ReturnTypeException
from dkist_header_validator.exceptions import ValidationException


def test_spec122_return_BytesIO_without_data(valid_spec_122_no_file):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header, no data attached
    When: Validating headers
    Then: Raise return type exception
    """
    # raises exception on failure
    with pytest.raises(ReturnTypeException):
        result = spec122_validator.validate(
            valid_spec_122_no_file, return_type=BytesIO, extra=False
        )
        assert isinstance(result, BytesIO)


def test_spec122_return_file_without_data(valid_spec_122_no_file):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header, no data attached
    When: Validating headers
    Then: raise a return type exception
    """
    # raises exception on failure
    with pytest.raises(ReturnTypeException):
        result = spec122_validator.validate(valid_spec_122_no_file, return_type=Path, extra=False)
        assert isinstance(result, Path)


def test_spec122_invalid_headers(invalid_spec_122_object):
    """
    Validates an invalid fits header against the SPEC-0122 schema
    Given: A invalid SPEC-0122 fits header
    When: Validating headers
    Then: raise a Spec122ValidationException
    """
    with pytest.raises(Spec122ValidationException):
        spec122_validator.validate(invalid_spec_122_object)


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
    Then: raise a Spec122ValidationException
    """

    with pytest.raises(ValidationException):
        spec122_validator.validate(invalid_file_param)


def test_toomanyHDUs_translate_to_214_l0(valid_spec_122_too_many_HDUs):
    """
    Validates headers with too many (more than 2) HDUs
    Given: A valid SPEC-122 file or HDUList with more than two headers
    When: Validating and translating headers
    Then: Raise an exception
    """
    # raises exception on failure
    with pytest.raises(ValidationException):
        spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_too_many_HDUs)


def test_toomanyHDUs_validate(valid_spec_122_too_many_HDUs):
    """
    Validates headers with too many (more than 2) HDUs
    Given: A valid SPEC-122 file or HDUList with more than two headers
    When: Validating headers
    Then: Raise an exception
    """
    # raises exception on failure
    with pytest.raises(ValidationException):
        spec122_validator.validate(valid_spec_122_too_many_HDUs)


@pytest.mark.parametrize("instrument", ["cryo-nirsp", "dlnirsp", "vbi", "visp", "vtf"])
def test_instrument_required_key_missing(invalid_instrument_table_spec_122_object):
    """
    Given: Headers from a specific instrument, but with one of the required header keys removed
    When: Validating headers
    Then: The correct Error is raised
    """
    fits_object, missing_key = invalid_instrument_table_spec_122_object
    with pytest.raises(
        Spec122ValidationException, match=f"'{missing_key}': 'required key not provided"
    ):
        spec122_validator.validate(fits_object)
