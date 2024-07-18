from io import BytesIO
from pathlib import Path

import pytest
from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList

from dkist_header_validator import ReturnTypeException
from dkist_header_validator import spec122_validator
from dkist_header_validator import Spec122ValidationException


def test_translate_spec122_to_214_l0_base(valid_spec_122_object):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return translated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_object)


def test_translate_required_only_headers_to_l0(valid_spec_122_object_required_only):
    """
    Validates and translates a spec122 compliant header with only the keywords required by the DC
    Given: A spec122 compliant header with only required keywords
    When: Validating and translating headers
    Then: return a translated 214l0 HDUList and do not raise an exception
    """
    spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_object_required_only)


def test_translate_expected_only_headers_to_l0(valid_spec_122_object_expected_only):
    """
    Validates and translates a spec122 compliant header with only the keywords expected by the DC
    Given: A spec122 compliant header with only expected keywords
    When: Validating and translating headers
    Then: return a translated 214l0 HDUList and do not raise an exception
    """
    spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_object_expected_only)


def test_translate_spec122_to_214_l0_return_dictionary(
    valid_spec_122_object,
):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return translated dictionary and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_object, return_type=dict
    )
    assert isinstance(result, dict)


def test_translate_spec122_to_214_l0_return_header(
    valid_spec_122_object,
):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return translated fits.header.Header object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_object, return_type=fits.header.Header
    )
    assert isinstance(result, fits.header.Header)


def test_translate_spec122_to_214_l0_return_bytesio(valid_spec_122_file):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return translated BytesIO object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_file, return_type=BytesIO
    )
    assert isinstance(result, BytesIO)


def test_translate_spec122_to_214_l0_return_hdu(valid_spec_122_file):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return translated PrimaryHDU object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_file, return_type=fits.PrimaryHDU
    )
    assert isinstance(result, fits.PrimaryHDU)


def test_translate_spec122_to_214_l0_return_file(valid_spec_122_file):
    """
    Validates and tries to translate a fits file against the SPEC-122 schema
    Given: A valid SPEC-122 fits file
    When: Validating file
    Then: return translated file object and do not raise an exception
    """
    # raises exception on failure
    result = spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_file, return_type=Path
    )
    assert isinstance(result, Path)


def test_spec122_to_214_l0_extrakeys_allowed(valid_spec_122_object_extra_keys):
    """
    Validates a fits header against the SPEC-0122 schema
    Given: A valid SPEC-0122 fits header with extra keys
    When: Validating headers
    Then: return HDUList and do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_object_extra_keys)


def test_spec122_to_214_l0_valid_extrakeys_not_allowed(valid_spec_122_object_extra_keys):
    """
    Validates a fits header against the SPEC-0122 schema
    Given: A valid SPEC-0122 fits header with extra keys
    When: Validating headers
    Then: Raise a Spec122ValidationException
    """
    with pytest.raises(Spec122ValidationException):
        spec122_validator.validate_and_translate_to_214_l0(
            valid_spec_122_object_extra_keys, extra=False
        )


def test_translate_compressed_spec122_to_214_l0(valid_spec_122_compressed):
    """
    Validates and translates a compressed spec122 compliant file
    Given: A valid compressed SPEC-0122 file
    When: Validating headers
    Then: return valid HDUList and do not raise an exception
    """
    result = spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_compressed)
    assert isinstance(result, fits.HDUList)


def test_visp_translate_to_214_l0(valid_spec_122_visp):
    """
    Validates a visp fits header against the SPEC-122 schema
    Given: A valid visp SPEC-122 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_visp, return_type=dict)


def test_translate_to_214_l0_return_primaryhdu(valid_spec_122_file):
    """
    Validates a fits file against the SPEC-122 schema
    Given: A valid SPEC-122 fits file
    When: Validating and translating headers
    Then: return validated PrimaryHDU and do not raise an exception
    """
    # raises exception on failure
    spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_file, return_type=fits.PrimaryHDU
    )


def test_translate_to_214_l0_return_primaryhdu_fail(valid_spec_122_no_file):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema
    Given: A valid visp SPEC-122 fits header
    When: Validating headers
    Then: Raise a Spec122ValidationException
    """
    with pytest.raises(ReturnTypeException):
        spec122_validator.validate_and_translate_to_214_l0(
            valid_spec_122_no_file, return_type=fits.PrimaryHDU
        )


def test_translate_to_214_l0_datainsecondhdu(valid_spec_122_second_hdu):
    """
    Validates headers with data stored in second HDU
    Given: A valid SPEC-122 file or with data stored in second HDU
    When: Validating and translating headers
    Then: Raise an exception
    """
    # raises exception on failure
    spec122_validator.validate_and_translate_to_214_l0(valid_spec_122_second_hdu, return_type=Path)


def test_translate_spec122_to_214_l0_check_remaining_122_keys(valid_spec_122_dict_only):
    """
    Validates and tries to translate a fits header against the SPEC-122 schema.
    Checks to make sure that no original 122 keys were dropped.
    Given: A valid SPEC-122 fits header
    When: Validating headers
    Then: return translated HDUList and do not raise an exception
    """
    # raises exception on failure
    hdr = spec122_validator.validate_and_translate_to_214_l0(
        valid_spec_122_dict_only, return_type=dict
    )
    for key in valid_spec_122_dict_only.keys():
        if key not in hdr.keys():
            raise KeyError(f" Keyword {key!r} from original header dropped during translation!")


def test_translate_bytesio_spec122_to_214_l0_return_primaryhdu(valid_spec_122_hdulist_only):
    """
    Validates and tries to translate a BytesIO object to a 214 l0 PrimaryHDU.
    Given: A valid SPEC-122 BytesIO object
    When: Validating and translating headers
    Then: return translated PrimaryHDU and do not raise an exception
    """

    target = BytesIO()
    valid_spec_122_hdulist_only.writeto(
        target, output_verify="exception", overwrite=True, checksum=True
    )
    target.seek(0)
    spec122_validator.validate_and_translate_to_214_l0(
        input_headers=target, return_type=fits.PrimaryHDU, extra=True
    )
