from pathlib import Path
from random import choice
from uuid import uuid4

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_data_simulator.spec214 import Spec214Dataset
from dkist_fits_specifications.spec122 import load_spec122
from dkist_fits_specifications.spec214 import load_spec214
from dkist_fits_specifications.spec214.level0 import load_level0_spec214

FITS_OBJECT_TYPES = [
    "fits",
    "dict",
    "hdulist",
    "header",
    "multiple_fits_cards_fits",
    "multiple_fits_cards_hdulist",
    "multiple_fits_cards_header",
]


def get_fits_object(
    object_type: str, tmpdir: Path, ds, required_only: bool = False, expected_only: bool = False
) -> str | dict | fits.HDUList | fits.header.Header:
    """
    Build up the required object type from the given simulated Dataset

    TYPES
    -----
    fits : a fits file on disk
    compressed : a compressed fits file on disk
    dict : headers formatted as a python dict
    hdulist : headers built into a PrimaryHDU presented in an HDUList
    header : headers formatted as a fits.header.Header
    second_hdu: a fits file on disk with the headers located in the second hdu

    multiple_fits_cards_fits: a fits file on disk that has multiple fits_cards
    multiple_fits_cards_hdulist: headers built into a PrimaryHDU presented in an HDUList with multiple fits_cards
    multiple_fits_cards_header: headers formatted as a fits.header.Header with multiple fits_cards
    """
    header_dict = [d.header(required_only=required_only, expected_only=expected_only) for d in ds][
        0
    ]
    data = np.ones(shape=ds.array_shape)
    hdu = fits.PrimaryHDU(data=data)
    for key, value in header_dict.items():
        hdu.header[key] = value

    if object_type == "fits":
        file_name = tmpdir / f"{uuid4().hex}.fits"
        hdu_list = fits.HDUList([hdu])
        hdu_list.writeto(str(file_name))
        return str(file_name)

    if object_type == "compressed":
        file_name = tmpdir / f"{uuid4().hex}.fits"
        hdu_list = fits.HDUList(
            [fits.PrimaryHDU(), fits.CompImageHDU(data=data, header=hdu.header)]
        )
        hdu_list.writeto(str(file_name))
        return str(file_name)

    if object_type == "dict":
        return header_dict

    if object_type == "hdulist":
        return fits.HDUList([hdu])

    if object_type == "header":
        return hdu.header

    if object_type == "second_hdu":
        file_name = tmpdir / f"{uuid4().hex}.fits"
        hdu_list = fits.HDUList([fits.PrimaryHDU(), fits.ImageHDU(data=data, header=hdu.header)])
        hdu_list.writeto(str(file_name))
        return str(file_name)

    if object_type == "third_hdu":
        file_name = tmpdir / f"{uuid4().hex}.fits"
        hdu_list = fits.HDUList(
            [
                fits.PrimaryHDU(),
                fits.ImageHDU(data=data, header=hdu.header),
                fits.ImageHDU(data=data, header=hdu.header),
            ]
        )
        hdu_list.writeto(str(file_name))
        return str(file_name)

    history_card1 = "history card 1"
    history_card2 = "history card 2"
    hdu.header.add_history(history_card1)
    hdu.header.add_history(history_card2)
    if object_type == "multiple_fits_cards_header":
        return hdu.header

    hdu_list = fits.HDUList([hdu])
    if object_type == "multiple_fits_cards_hdulist":
        return hdu_list

    if object_type == "multiple_fits_cards_fits":
        file_name = tmpdir / f"{uuid4().hex}.fits"
        hdu_list.writeto(str(file_name))
        return str(file_name)


class BaseSpec122Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_122_object(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function", params=["dict", "header", "multiple_fits_cards_header"])
def valid_translator_object(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_122_object_required_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset(), required_only=True
    )


@pytest.fixture(scope="function", params=["dict", "header"])
def valid_translator_object_required_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset(), required_only=True
    )


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_122_object_expected_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset(), expected_only=True
    )


@pytest.fixture(scope="function", params=["dict", "header"])
def valid_translator_object_expected_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset(), expected_only=True
    )


@pytest.fixture(scope="function")
def valid_spec_122_file(tmpdir):
    yield get_fits_object(object_type="fits", tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function")
def valid_spec_122_compressed(tmpdir):
    yield get_fits_object(object_type="compressed", tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_122_visp(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset(instrument="visp")
    )


@pytest.fixture(scope="function", params=["dict", "header", "hdulist"])
def valid_spec_122_no_file(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function")
def valid_spec_122_dict_only(tmpdir):
    yield get_fits_object(object_type="dict", tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function")
def valid_spec_122_hdulist_only(tmpdir):
    yield get_fits_object(object_type="hdulist", tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function")
def valid_spec_122_second_hdu(tmpdir):
    yield get_fits_object(object_type="second_hdu", tmpdir=tmpdir, ds=BaseSpec122Dataset())


@pytest.fixture(scope="function")
def valid_spec_122_too_many_HDUs(tmpdir):
    yield get_fits_object(object_type="third_hdu", tmpdir=tmpdir, ds=BaseSpec122Dataset())


class Spec122DatasetExtraKeys(BaseSpec122Dataset):
    def __init__(self):
        super().__init__()
        self.add_constant_key("XTRAKEY1", "ABCDEFG")
        self.add_constant_key("XTRAKEY2", "HIJKLMN")
        self.add_constant_key("XTRAKEY3", "OPQRSTU")
        self.add_constant_key("XTRAKEY4", "VWXYZAB")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_122_object_extra_keys(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=Spec122DatasetExtraKeys())


class InvalidBaseSpec122Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )
        self.add_remove_key("NAXIS1")
        self.add_remove_key("NXAIS2")
        self.add_remove_key("WAVELNTH")
        self.add_remove_key("DATE-OBS")
        self.add_remove_key("ID___002")
        self.add_remove_key("ID___003")
        self.add_remove_key("ID___012")
        self.add_remove_key("DKIST003")
        self.add_remove_key("DKIST004")
        self.add_remove_key("HISTORY")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_spec_122_object(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=InvalidBaseSpec122Dataset())


class InvalidInstrumentTableSpec122Dataset(BaseSpec122Dataset):
    def __init__(self, instrument: str):
        super().__init__(instrument=instrument)

        # Remove a random key from the instrument table
        glob_name = instrument.lower().replace(
            "-", ""
        )  # For cryo and dl b/c the yamls don't have dashes
        instrument_keys = load_spec122(glob=glob_name)[glob_name]
        removal_candidates = [k for k, v in instrument_keys.items() if "instrument_required" in v]
        removed_key = choice(removal_candidates)
        self.add_remove_key(removed_key)
        self.removed_key = removed_key


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_instrument_table_spec_122_object(tmpdir, request, instrument):
    dataset = InvalidInstrumentTableSpec122Dataset(instrument)
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=dataset), dataset.removed_key


class BaseSpec122DatasetCaseSensitive(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )
        self.add_constant_key("DKIST004", "oBSErve")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_122_casesensitive(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec122DatasetCaseSensitive()
    )


class BaseSpec214l0Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214l0_object(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214l0_object_required_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214l0Dataset(), required_only=True
    )


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214l0_object_expected_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214l0Dataset(), expected_only=True
    )


@pytest.fixture(scope="function")
def valid_spec_214l0_file(tmpdir):
    yield get_fits_object(object_type="fits", tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function")
def valid_spec_214l0_compressed(tmpdir):
    yield get_fits_object(object_type="compressed", tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214l0_visp(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214l0Dataset(instrument="visp")
    )


@pytest.fixture(scope="function", params=["dict", "header", "hdulist"])
def valid_spec_214l0_no_file(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function")
def valid_spec_214l0_dict_only(tmpdir):
    yield get_fits_object(object_type="dict", tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function")
def valid_spec_214l0_hdulist_only(tmpdir):
    yield get_fits_object(object_type="hdulist", tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function")
def valid_spec_214l0_second_hdu(tmpdir):
    yield get_fits_object(object_type="second_hdu", tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


@pytest.fixture(scope="function")
def valid_spec_214_l0_too_many_HDUs(tmpdir):
    yield get_fits_object(object_type="third_hdu", tmpdir=tmpdir, ds=BaseSpec214l0Dataset())


class Spec214l0DatasetExtraKeys(BaseSpec214l0Dataset):
    def __init__(self):
        super().__init__()
        self.add_constant_key("XTRAKEY1", "ABCDEFG")
        self.add_constant_key("XTRAKEY2", "HIJKLMN")
        self.add_constant_key("XTRAKEY3", "OPQRSTU")
        self.add_constant_key("XTRAKEY4", "VWXYZAB")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214l0_object_extra_keys(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=Spec214l0DatasetExtraKeys())


class InvalidBaseSpec214l0Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )
        self.add_remove_key("NAXIS1")
        self.add_remove_key("NXAIS2")
        self.add_remove_key("LINEWAV")
        self.add_remove_key("DATE-OBS")
        self.add_remove_key("FILE_ID")
        self.add_remove_key("EXPER_ID")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_spec_214l0_object(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=InvalidBaseSpec214l0Dataset()
    )


@pytest.fixture(scope="function")
def invalid_spec_214l0_compressed(tmpdir):
    yield get_fits_object(object_type="compressed", tmpdir=tmpdir, ds=InvalidBaseSpec214l0Dataset())


class InvalidInstrumentTableSpec214l0Dataset(BaseSpec214l0Dataset):
    def __init__(self, instrument: str):
        super().__init__(instrument=instrument)

        # Remove a random key from the instrument table
        glob_name = instrument.lower().replace(
            "-", ""
        )  # For cryo and dl b/c the yamls don't have dashes
        instrument_keys = load_level0_spec214(glob=glob_name)[glob_name]
        removal_candidates = [k for k, v in instrument_keys.items() if "instrument_required" in v]
        removed_key = choice(removal_candidates)
        self.add_remove_key(removed_key)
        self.removed_key = removed_key


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_instrument_table_spec_214l0_object(tmpdir, request, instrument):
    dataset = InvalidInstrumentTableSpec214l0Dataset(instrument)
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=dataset), dataset.removed_key


class BaseSpec214l0DatasetCaseSensitive(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )
        self.add_constant_key("VBISYNCM", "fIxED")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214l0_casesensitive(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214l0DatasetCaseSensitive()
    )


class BaseSpec214Dataset(Spec214Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )

    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214_object(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214_object_required_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214Dataset(), required_only=True
    )


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214_object_expected_only(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214Dataset(), expected_only=True
    )


@pytest.fixture(scope="function")
def valid_spec_214_file(tmpdir):
    yield get_fits_object(object_type="fits", tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function")
def valid_spec_214_compressed(tmpdir):
    yield get_fits_object(object_type="compressed", tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214_visp(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214Dataset(instrument="visp")
    )


@pytest.fixture(
    scope="function", params=["dict", "header", "hdulist", "multiple_fits_cards_header"]
)
def valid_spec_214_no_file(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function")
def valid_spec_214_dict_only(tmpdir):
    yield get_fits_object(object_type="dict", tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function")
def valid_spec_214_hdulist_only(tmpdir):
    yield get_fits_object(object_type="hdulist", tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function")
def valid_spec_214_second_hdu(tmpdir):
    yield get_fits_object(object_type="second_hdu", tmpdir=tmpdir, ds=BaseSpec214Dataset())


@pytest.fixture(scope="function")
def valid_spec_214_too_many_HDUs(tmpdir):
    yield get_fits_object(object_type="third_hdu", tmpdir=tmpdir, ds=BaseSpec214Dataset())


class Spec214DatasetExtraKeys(BaseSpec214Dataset):
    def __init__(self):
        super().__init__()
        self.add_constant_key("XTRAKEY1", "ABCDEFG")
        self.add_constant_key("XTRAKEY2", "HIJKLMN")
        self.add_constant_key("XTRAKEY3", "OPQRSTU")
        self.add_constant_key("XTRAKEY4", "VWXYZAB")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214_object_extra_keys(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=Spec214DatasetExtraKeys())


class InvalidBaseSpec214Dataset(Spec214Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )
        self.add_remove_key("NAXIS1")
        self.add_remove_key("NXAIS2")
        self.add_remove_key("LINEWAV")
        self.add_remove_key("DATE-OBS")
        self.add_remove_key("FILE_ID")
        self.add_remove_key("EXPER_ID")

    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_spec_214_object(tmpdir, request):
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=InvalidBaseSpec214Dataset())


@pytest.fixture(scope="function")
def invalid_spec_214_compressed(tmpdir):
    yield get_fits_object(object_type="compressed", tmpdir=tmpdir, ds=InvalidBaseSpec214Dataset())


class BaseSpec214DatasetCaseSensitive(Spec214Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )
        self.add_constant_key("VBISYNCM", "fIxED")

    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def valid_spec_214_casesensitive(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=BaseSpec214DatasetCaseSensitive()
    )


class InvalidPolarimetricSpec214Dataset(BaseSpec214Dataset):
    def __init__(self):
        super().__init__(instrument="visp")
        self.add_constant_key("VSPPOLMD", "observe_polarimetric")
        self.add_remove_key("POL_SENS")


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_polarimetric_spec_214_object(tmpdir, request):
    yield get_fits_object(
        object_type=request.param, tmpdir=tmpdir, ds=InvalidPolarimetricSpec214Dataset()
    )


class InvalidInstrumentTableSpec214Dataset(BaseSpec214Dataset):
    def __init__(self, instrument: str):
        super().__init__(instrument=instrument)

        # Remove a random key from the instrument table
        glob_name = instrument.lower().replace(
            "-", ""
        )  # For cryo and dl b/c the yamls don't have dashes
        instrument_keys = load_spec214(glob=glob_name)[glob_name]
        removal_candidates = [k for k, v in instrument_keys.items() if "instrument_required" in v]
        removed_key = choice(removal_candidates)
        self.add_remove_key(removed_key)
        self.removed_key = removed_key


@pytest.fixture(scope="function", params=FITS_OBJECT_TYPES)
def invalid_instrument_table_spec_214_object(tmpdir, request, instrument):
    dataset = InvalidInstrumentTableSpec214Dataset(instrument)
    yield get_fits_object(object_type=request.param, tmpdir=tmpdir, ds=dataset), dataset.removed_key
