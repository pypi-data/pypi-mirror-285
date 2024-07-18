from io import BytesIO
from pathlib import Path

from astropy.io import fits
from dkist_fits_specifications.utils.formatter import reformat_spec214_header

from dkist_header_validator import spec214_l0_validator
from dkist_header_validator import spec214_validator


def test_spec214l0(valid_spec_214l0_object):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214l0 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_object, extra=False)


def test_spec214(valid_spec_214_object):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_object, extra=False)


def test_spec214l0_return_dictionary(valid_spec_214l0_object):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated dictionary and do not raise an exception
    """
    # raises exception on failure
    result = spec214_l0_validator.validate(valid_spec_214l0_object, return_type=dict, extra=False)
    assert isinstance(result, dict)


def test_spec214_return_dictionary(valid_spec_214_object):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated dictionary and do not raise an exception
    """
    # raises exception on failure
    result = spec214_validator.validate(valid_spec_214_object, return_type=dict, extra=False)
    assert isinstance(result, dict)


def test_spec214l0_return_fits_header(valid_spec_214l0_object):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated fits.header.Header object and do not raise an exception
    """
    # raises exception on failure
    result = spec214_l0_validator.validate(
        valid_spec_214l0_object, return_type=fits.header.Header, extra=False
    )
    assert isinstance(result, fits.header.Header)


def test_spec214_return_fits_header(valid_spec_214_object):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated fits.header.Header object and do not raise an exception
    """
    # raises exception on failure
    result = spec214_validator.validate(
        valid_spec_214_object, return_type=fits.header.Header, extra=False
    )
    assert isinstance(result, fits.header.Header)


def test_spec214l0_return_HDU(valid_spec_214l0_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated fits.PrimaryHDU object and do not raise an exception
    """
    # raises exception on failure
    result = spec214_l0_validator.validate(
        valid_spec_214l0_file, return_type=fits.PrimaryHDU, extra=False
    )
    assert isinstance(result, fits.PrimaryHDU)


def test_spec214_return_HDU(valid_spec_214_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated fits.PrimaryHDU object and do not raise an exception
    """
    # raises exception on failure
    result = spec214_validator.validate(
        valid_spec_214_file, return_type=fits.PrimaryHDU, extra=False
    )
    assert isinstance(result, fits.PrimaryHDU)


def test_spec214l0_return_BytesIO(valid_spec_214l0_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated BytesIO object and do not raise an exception
    """
    # raises exception on failure
    result = spec214_l0_validator.validate(valid_spec_214l0_file, return_type=BytesIO, extra=False)
    assert isinstance(result, BytesIO)


def test_spec214_return_BytesIO(valid_spec_214_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated BytesIO object and do not raise an exception
    """
    # raises exception on failure
    result = spec214_validator.validate(valid_spec_214_file, return_type=BytesIO, extra=False)
    assert isinstance(result, BytesIO)


def test_spec214l0_return_file(valid_spec_214l0_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated file and do not raise an exception
    """
    # raises exception on failure
    result = spec214_l0_validator.validate(valid_spec_214l0_file, return_type=Path, extra=False)
    assert isinstance(result, Path)


def test_spec214_return_file(valid_spec_214_file):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated file and do not raise an exception
    """
    # raises exception on failure
    result = spec214_validator.validate(valid_spec_214_file, return_type=Path, extra=False)
    assert isinstance(result, Path)


def test_spec214l0_extraheaders_allowed(valid_spec_214l0_object_extra_keys):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_object_extra_keys)


def test_spec214_extraheaders_allowed(valid_spec_214_object_extra_keys):
    """
    Validates a fits header against the SPEC-0214 schema
    Given: A valid SPEC-0214 fits header
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_object_extra_keys)


def test_validatel0_required_only_headers(valid_spec_214l0_object_required_only):
    """
    Validates a spec214l0 compliant header with only the keywords required by the DC
    Given: A spec214l0 compliant header with only required keywords
    When: Validating headers
    Then: return a validated HDUList and do not raise an exception
    """
    spec214_l0_validator.validate(valid_spec_214l0_object_required_only)


def test_validate_required_only_headers(valid_spec_214_object_required_only):
    """
    Validates a spec214 compliant header with only the keywords required by the DC
    Given: A spec214 compliant header with only required keywords
    When: Validating headers
    Then: return a validated HDUList and do not raise an exception
    """
    spec214_validator.validate(valid_spec_214_object_required_only)


def test_validatel0_expected_only_headers(valid_spec_214l0_object_expected_only):
    """
    Validates a spec214l0 compliant header with only the keywords required by the DC
    Given: A spec214l0 compliant header with only required keywords
    When: Validating headers
    Then: return a validated HDUList and do not raise an exception
    """
    spec214_l0_validator.validate(valid_spec_214l0_object_expected_only)


def test_validate_expected_only_headers(valid_spec_214_object_expected_only):
    """
    Validates a spec214 compliant header with only the keywords required by the DC
    Given: A spec214 compliant header with only required keywords
    When: Validating headers
    Then: return a validated HDUList and do not raise an exception
    """
    spec214_validator.validate(valid_spec_214_object_expected_only)


def test_compressed_spec214l0(valid_spec_214l0_compressed):
    """
    Validates a compressed spec214 compliant file
    Given: A valid compressed SPEC-0214 file
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    spec214_l0_validator.validate(valid_spec_214l0_compressed)


def test_compressed_spec214(valid_spec_214_compressed):
    """
    Validates a compressed spec214 compliant file
    Given: A valid compressed SPEC-0214 file
    When: Validating headers
    Then: return validated HDUList and do not raise an exception
    """
    spec214_validator.validate(valid_spec_214_compressed)


def test_validatel0_datainsecondHDU(valid_spec_214l0_second_hdu):
    """
    Validates headers with data stored in second HDU
    Given: A valid SPEC-214 file or with data stored in second HDU
    When: Validating headers
    Then: Raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_second_hdu, return_type=Path)


def test_validate_datainsecondHDU(valid_spec_214_second_hdu):
    """
    Validates headers with data stored in second HDU
    Given: A valid SPEC-214 file or with data stored in second HDU
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_second_hdu, return_type=Path)


def test_validate_s214l0_visp(valid_spec_214l0_visp):
    """
    Validates headers with visp headers and data
    Given: A valid SPEC-214 visp file
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_visp)


def test_validate_s214_visp(valid_spec_214_visp):
    """
    Validates headers with visp headers and data
    Given: A valid SPEC-214 visp file
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_visp)


def test_validate_s214l0_no_file(valid_spec_214l0_no_file):
    """
    Validates headers of the type hdulist, dict, or fits.Header
    Given: A valid SPEC-214 header
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_no_file)


def test_validate_s214_no_file(valid_spec_214_no_file):
    """
    Validates headers of the type hdulist, dict, or fits.Header
    Given: A valid SPEC-214 header
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_no_file)


def test_validate_s214l0_dict_only(valid_spec_214l0_dict_only):
    """
    Validates a dict of input S214 headers
    Given: A valid SPEC-214 header
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_dict_only)


def test_validate_s214_dict_only(valid_spec_214_dict_only):
    """
    Validates a dict of input S214 headers
    Given: A valid SPEC-214 header
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_dict_only)


def test_validate_s214l0_hdulist_only(valid_spec_214l0_hdulist_only):
    """
    Validates an HDUList of input S214 headers
    Given: A valid SPEC-214 header
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_hdulist_only)


def test_validate_s214_hdulist_only(valid_spec_214_hdulist_only):
    """
    Validates an HDUList of input S214 headers
    Given: A valid SPEC-214 header
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_hdulist_only)


def test_validate_s214l0_casesensitive(valid_spec_214l0_casesensitive):
    """
    Validates headers with a keyword that will need a case sensitive change
    Given: S214 headers with a keyword that will need a case sensitive change
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_l0_validator.validate(valid_spec_214l0_casesensitive)


def test_validate_s214_casesensitive(valid_spec_214_casesensitive):
    """
    Validates headers with a keyword that will need a case sensitive change
    Given: S214 headers with a keyword that will need a case sensitive change
    When: Validating headers
    Then: Do not raise an exception
    """
    # raises exception on failure
    spec214_validator.validate(valid_spec_214_casesensitive)


def test_validate_formatted_compressed_header(tmp_path):
    """
    Validates a header which has been pretty-formatted by the formatter.
    Given: A formatted, compressed, fits file
    When: Validating Headers
    Then: Do not raise an exception.
    """
    from .conftest import BaseSpec214DatasetCaseSensitive, get_fits_object

    fits_file = get_fits_object(
        object_type="fits", tmpdir=tmp_path, ds=BaseSpec214DatasetCaseSensitive()
    )
    with fits.open(fits_file) as hdul:
        plain_header = hdul[0].header
        data = hdul[0].data

    # Generate a header with the compression keys
    hdu = fits.CompImageHDU(header=plain_header, data=data)
    # Format this header
    formatted_header = reformat_spec214_header(hdu._header)
    # Make a new HDU with the formatted header
    hdul = fits.HDUList(
        [fits.PrimaryHDU(), fits.CompImageHDU(header=formatted_header, data=hdu.data)]
    )
    hdul.writeto(tmp_path / "test.fits")

    # Validate the new formatted header
    spec214_validator.validate(tmp_path / "test.fits")
