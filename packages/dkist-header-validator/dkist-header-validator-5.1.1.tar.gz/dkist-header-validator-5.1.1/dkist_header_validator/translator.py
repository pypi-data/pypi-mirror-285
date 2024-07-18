import logging
from datetime import datetime
from functools import reduce
from typing import Any
from typing import IO

from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList
from dkist_fits_specifications.spec214 import level0
from dkist_fits_specifications.spec214 import load_processed_spec214
from dkist_fits_specifications.spec214 import load_spec214

logger = logging.getLogger(__name__)

__all__ = [
    "translate_spec122_to_spec214_l0",
    "sanitize_to_spec214_level1",
    "remove_extra_axis_keys",
]

type_map = {"int": int, "float": float, "str": str, "bool": bool}


def translate_spec122_to_spec214_l0(
    spec122_input: HDUList | dict | fits.header.Header | str | IO | list,
) -> dict | HDUList:
    """
    Convert spec 122 headers to spec 214 l0 headers

    Parameters
    ----------
    spec122_input
        Spec 122 headers or headers + data to convert
    Returns
    -------
    spec214 l0 headers and (possibly) data
    """
    # extract headers and data
    input_headers, input_data = _parse_fits_like_input(spec122_input)
    # convert headers
    output_headers = _add_214_l0_headers(input_headers)
    # update DATE keyword
    output_headers["DATE"] = datetime.now().isoformat()
    if input_data is not None:  # return hdu list if the input had data
        return _format_output_hdu(output_headers, input_data)
    return output_headers  # return headers if only headers were given


def sanitize_to_spec214_level1(
    input_headers: HDUList | dict | fits.header.Header | str | IO | list,
) -> dict | HDUList:
    """
    Remove all non-214 compliant header values

    Parameters
    ----------
    input_headers
        Spec 214 headers or headers + data to convert
    Returns
    -------
        spec214 l1 headers and (possibly) data
    """
    # extract headers and data
    input_headers, input_data = _parse_fits_like_input(input_headers)
    header = fits.Header(input_headers)
    # convert headers
    expanded_214 = load_processed_spec214(**dict(input_headers))
    all_214_keys = reduce(list.__add__, map(list, expanded_214.values()))

    for keyword in tuple(header.keys()):
        if keyword not in all_214_keys:
            header.remove(keyword)

    if input_data is not None:  # return hdu list if the input had data
        return _format_output_hdu(header, input_data)
    return header  # return headers if only headers were given


def remove_extra_axis_keys(
    input_headers: HDUList | dict | fits.header.Header | str | IO | list,
) -> dict | HDUList:
    """
    Remove all keywords that refer to axes that don't exist in the data array

    Parameters
    ----------
    input_headers
        Spec 214 headers or headers + data
    Returns
    -------
    Stripped headers and (possibly) data
    """
    # extract headers and data
    input_headers, input_data = _parse_fits_like_input(input_headers)
    header = fits.Header(input_headers)

    # Get a list of all unexpanded keywords that have "n" in them
    all_keys = reduce(list.__add__, map(list, load_spec214().values()))
    n_keys = [i for i in all_keys if "n" in i]

    # Remove all keywords where "n" is substituted by a larger number than NAXIS
    for n_key in n_keys:
        for i in range(header["NAXIS"] + 1, 6):
            expanded_key = n_key.replace("n", str(i))
            header.pop(expanded_key, None)

    if input_data is not None:  # return hdu list if the input had data
        return _format_output_hdu(header, input_data)
    return header  # return headers if only headers were given


def _parse_fits_like_input(
    spec122_input: HDUList | dict | fits.header.Header | str | IO | list,
) -> tuple[fits.Header, bytes | None]:
    """
    Parse out a header and optional data from the various types of input
    """
    if isinstance(spec122_input, dict):
        return fits.Header(spec122_input), None
    if isinstance(spec122_input, fits.header.Header):
        return spec122_input, None
    if isinstance(spec122_input, HDUList):
        try:
            return spec122_input[1].header, spec122_input[1].data
        except IndexError:  # non-compressed
            return spec122_input[0].header, spec122_input[0].data

    # If headers are of any other type, see if it is a file and try to open that
    try:  # compressed
        with fits.open(spec122_input) as hdus:
            return hdus[1].header, hdus[1].data
    except IndexError:  # non-compressed
        with fits.open(spec122_input) as hdus:
            return hdus[0].header, hdus[0].data


def _format_output_hdu(hdr, data) -> HDUList:
    new_hdu = fits.PrimaryHDU(data)
    hdu_list = fits.HDUList([new_hdu])
    for key, value in hdr.items():
        hdu_list[0].header[key] = value
    return hdu_list


def _add_214_l0_headers(header: dict[str, Any] | fits.Header):
    """
    Translates 122 keywords to 214 l0 keywords and returns a dictionary
    """
    result = {}  # output headers

    # We need an extra layer of sanitation here because `load_level0_spec214` is a cached function
    # and the weird header cards are not hashable
    sanitized_header = {
        k: v for k, v in header.items() if not isinstance(v, fits.header._HeaderCommentaryCards)
    }

    # Passing only INSTRUME=header["INSTRUME"] is a hack for speed. We know that right now the only schema processor
    # that gets applied to 122 or 214 level0 schema (this happens in `load_level0_spec214`) is the instrument requiredness
    # processor. Thus, we only need to pass a header consisting of `{INSTRUME: sanitized_header["INSTRUME"]}`.
    # This results in a massive speed increase during translation because `load_level0_spec214` is cached. If we pass
    # the whole header then each file will result in a new call to this function, but if we only pass the instrument
    # then we only make new calls to `load_level0_spec214` at most 5 times (for each DKIST instrumet).
    spec214_l0_schema_sections = level0.load_level0_spec214(
        INSTRUME=sanitized_header.get("INSTRUME", "None")
    ).values()
    flat_spec214_l0_schema = {
        key: schema
        for definition in spec214_l0_schema_sections
        for (key, schema) in definition.items()
    }

    # translate 122 -> 214 headers
    for key, key_schema in flat_spec214_l0_schema.items():
        result.update(_translate_key(key, key_schema, header))

    # add remaining header values to result
    hdr_keys_not_translated = {k: v for k, v in header.items() if k not in result}
    result.update(hdr_keys_not_translated)
    return result


def _translate_key(key, key_schema, hdr) -> dict:
    default_values = {"str": "default", "int": -999, "float": -999.9, "bool": False}
    key_is_copied = key_schema.get("copy")
    copy_schema_only = key_schema.get("copy") == "schema"
    key_is_renamed = key_schema.get("rename")
    renamed_key_is_in_header = key_is_renamed and (key_is_renamed in hdr)
    key_is_required = key_schema.get("required")
    key_is_in_header = key in hdr

    if copy_schema_only and key_is_in_header:
        return {key: default_values[key_schema["type"]]}
    if key_is_copied and key_is_in_header:
        return {key: hdr[key]}
    if key_is_copied and not key_is_in_header and renamed_key_is_in_header:
        return {key: hdr[key_schema.get("rename")]}
    if (
        key_is_copied
        and not key_is_in_header
        and key_is_renamed
        and not renamed_key_is_in_header
        and key_is_required
    ):
        raise KeyError(f" Required keyword {key!r} not found.")
    if key_is_copied and not key_is_in_header and not key_is_renamed and key_is_required:
        raise KeyError(f" Required keyword {key!r} not found.")
    if not key_is_copied and key_is_required and key_is_in_header:
        return {key: hdr[key]}
    if not key_is_copied and key_is_required and not key_is_in_header:
        return {key: default_values[key_schema["type"]]}
    # nothing to translate
    return {}
