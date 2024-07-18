from io import BytesIO
from pathlib import Path

from astropy.io import fits

from dkist_header_validator import spec122_validator


def test_spec122(valid_spec_122_object):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate(valid_spec_122_object, extra=False)


def test_spec122_return_dictionary(valid_spec_122_object):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return validated dictionary and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate(valid_spec_122_object, return_type=dict, extra=False)
    assert isinstance(result, dict)


def test_spec122_return_fits_header(valid_spec_122_object):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return validated fits.header.Header object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate(
        valid_spec_122_object, return_type=fits.header.Header, extra=False
    )
    assert isinstance(result, fits.header.Header)


def test_spec122_return_BytesIO(valid_spec_122_file):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return validated BytesIO object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate(valid_spec_122_file, return_type=BytesIO, extra=False)
    assert isinstance(result, BytesIO)


def test_spec122_return_HDU(valid_spec_122_file):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return validated PrimaryHDU object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate(
        valid_spec_122_file, return_type=fits.PrimaryHDU, extra=False
    )
    assert isinstance(result, fits.PrimaryHDU)


def test_spec122_return_file(valid_spec_122_file):
    """
    Validates a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return validated file and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate(valid_spec_122_file, return_type=Path, extra=False)
    assert isinstance(result, Path)


def test_validate_required_only_headers(valid_spec_122_object_required_only):
    """
    Validates a spec122 compliant header with only the keywords required by the DC
    Given: A spec122 compliant header with only required keywords
    When: Validating headers
    Then: return a validated HDUList and do not raise an exception
    """
    spec122_validator.validate(valid_spec_122_object_required_only)


def test_validate_expected_only_headers(valid_spec_122_object_expected_only):
    """
    Validates a spec122 compliant header with only the keywords expected by the DC
    Given: A spec122 compliant header with only exxpected keywords
    When: Validating headers
    Then: return a validated HDUList and do not raise an exception
    """
    spec122_validator.validate(valid_spec_122_object_expected_only)


def test_compressed_spec122_valid(valid_spec_122_compressed):
    """
    Validates a compressed spec122 compliant file
    Given: A valid compressed SPEC-0122 file
    When: Validating headers
    Then: return valid HDUList and do not raise an exception
    """
    spec122_validator.validate(valid_spec_122_compressed)


def test_visp_spec122(valid_spec_122_visp):
    """
    Validates a visp fits header against the SPEC-122 schema
    Given: A valid visp SPEC-122 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate(valid_spec_122_visp, extra=False)


def test_datainsecondHDU(valid_spec_122_second_hdu):
    """
    Validates headers with data stored in second HDU
    Given: A valid SPEC-122 file or with data stored in second HDU
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate(valid_spec_122_second_hdu, return_type=Path)


def test_casesensitivity(valid_spec_122_casesensitive):
    """
    Validates headers with a keyword that will need a case sensitive change
    Given: Headers with a keyword that will need a case sensitive change
    When: Validating headers
    Then: Do not raise and exception
    """
    # raises exception on failure
    spec122_validator.validate(valid_spec_122_casesensitive)
