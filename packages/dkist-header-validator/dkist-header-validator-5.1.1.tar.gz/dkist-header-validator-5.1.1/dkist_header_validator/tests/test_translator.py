import pytest
from astropy.io import fits

from dkist_header_validator.translator import sanitize_to_spec214_level1
from dkist_header_validator.translator import translate_spec122_to_spec214_l0


def test_spec122_to_214_l0_valid(valid_translator_object):
    """
    Strips headers down to a 214 L1 object
    Given: A valid SPEC-0122 object
    When: Sanitizing headers
    Then:
    """
    translate_spec122_to_spec214_l0(valid_translator_object)


def test_spec122_to_214_l0_missing_required_keys(invalid_spec_122_object):
    """
    Translates an invalid SPEC-0122 object missing required
    keys to a SPEC-214 l0 object
    Given: A valid SPEC-0122 object
    When: Translating headers
    Then: Raises a KeyError exception
    """
    with pytest.raises(KeyError):
        translate_spec122_to_spec214_l0(invalid_spec_122_object)


@pytest.mark.parametrize("instrument", ["vbi"])
def test_spec122_to_214_l0_missing_required_instrument_keys(
    invalid_instrument_table_spec_122_object,
):
    """
    Given: A SPEC-0122 object missing a required instrument key
    When: Translating headers
    Then: Raises a KeyError exception
    """
    invalid_obj, _ = invalid_instrument_table_spec_122_object
    with pytest.raises(KeyError):
        translate_spec122_to_spec214_l0(invalid_obj)


def test_translate_to_214_l0_required_only_headers(valid_translator_object_required_only):
    """
    Translates a spec122 compliant header with only the keywords required by the DC
    Given: A spec122 compliant header with only required keywords
    When: Translating headers
    Then: For a fits file input, return a HDUList and do not raise an exception
          For a dict, HDUList, or header input, return a dictionary and do not raise an exception
    """
    translate_spec122_to_spec214_l0(valid_translator_object_required_only)


def test_translate_to_214_l0_expected_only_headers(valid_translator_object_expected_only):
    """
    Translates a spec122 compliant header with only the keywords required by the DC
    Given: A spec122 compliant header with only required keywords
    When: Translating headers
    Then: For a fits file input, return a HDUList and do not raise an exception
          For a dict, HDUList, or header input, return a dictionary and do not raise an exception
    """
    translate_spec122_to_spec214_l0(valid_translator_object_expected_only)


# I removed all of the compressed tests because a file (compressed or not) cannot go directly into the translator.
# It has to go into the validator first, which will hand it to the translator in the right format


def test_sanitize_s122(valid_translator_object):
    """
    Tries to sanitize a Spec-0122 object
    Given: A valid SPEC-0122 object
    When: Stripping down headers to 214 L1 (no 122 headers)
    Then: Returns a header
    """
    sanitize_to_spec214_level1(valid_translator_object)


def test_sanitize_translated_s214l0(valid_translator_object):
    """
    Tries to sanitize a Spec-214 L0 object
    Given: A valid SPEC-0122 object
    When: Translating and stripping down headers to 214 L1 (no 122 headers)
    Then: Returns a header
    """
    s214_l0_header = translate_spec122_to_spec214_l0(valid_translator_object)
    isinstance(sanitize_to_spec214_level1(s214_l0_header), fits.Header)


def test_sanitize(valid_spec_214_no_file):
    """
    Sanitizes a SPEC-214 L1 object
    Given: A valid SPEC-214 L1 object
    When: Stripping down headers to 214 L1 (no 122 headers)
    Then: For a header or a dict, return a fits header and do not raise an exception
          For an HDUList or a file, return an HDUList and do not raise an exception
    """
    isinstance(sanitize_to_spec214_level1(valid_spec_214_no_file), fits.Header)
