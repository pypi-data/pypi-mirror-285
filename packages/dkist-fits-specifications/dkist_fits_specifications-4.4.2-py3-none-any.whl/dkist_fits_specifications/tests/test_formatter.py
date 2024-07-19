from random import randint

import pytest
from astropy.io import fits

from dkist_fits_specifications.spec214 import load_processed_spec214
from dkist_fits_specifications.utils.formatter import reformat_spec214_header


@pytest.fixture
def header_with_all_sections() -> fits.Header:
    all_214_schemas = load_processed_spec214()
    header_dict = dict()
    for section in all_214_schemas.values():
        # Value doesn't matter at all, so just make it a random int
        header_dict.update({k: randint(1, 10) for k in section.keys()})

    # Manual intervention needed on these keys so header processors will work correctly
    del header_dict["END"]
    header_dict["DAAXES"] = 3
    header_dict["DEAXES"] = 2
    header_dict["DNAXIS"] = 5
    header_dict["NPROPOS"] = 10
    header_dict["NEXPERS"] = 11
    header_dict["NAXIS"] = 3
    header_dict["ZVAL1"] = 1
    header_dict["TFIELDS"] = 2
    header_dict["NSPECLNS"] = 13
    return fits.Header(header_dict)


def test_formatter(header_with_all_sections):
    """
    Given: A 214 header with all possible schema sections
    When: Formatting the header
    Then: The dang thing runs
    """
    output_header = reformat_spec214_header(header_with_all_sections)
    assert isinstance(output_header, fits.Header)
