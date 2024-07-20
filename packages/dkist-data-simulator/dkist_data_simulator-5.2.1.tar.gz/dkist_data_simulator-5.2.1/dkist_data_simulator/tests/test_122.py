import pytest
from astropy.io import fits

from dkist_data_simulator.spec122 import Spec122Dataset


def test_generate_122():
    ds = Spec122Dataset(
        time_delta=10,
        dataset_shape=[16, 2048, 4096],
        array_shape=[1, 2048, 4096],
        instrument="vbi",
    )
    headers = ds.generate_headers(required_only=True)
    for h in headers:
        assert h["NAXIS"] == 3
        assert h["NAXIS1"] == 4096
        assert h["NAXIS2"] == 2048
        assert h["NAXIS3"] == 1
        assert h["INSTRUME"] == "VBI"
        assert "VBI__001" in h.keys()  # Instrument required for VBI


@pytest.mark.parametrize(
    "weird_header_cards",
    [
        pytest.param(False, id="No weird header cards"),
        pytest.param(True, id="With FITS comment cards"),
    ],
)
def test_generate_214_level0(weird_header_cards):
    additional_header = fits.Header()
    if weird_header_cards:
        additional_header.add_comment("Comment 1")
        additional_header.add_comment("Comment 2")
    ds = Spec122Dataset(
        time_delta=10,
        dataset_shape=[16, 2048, 4096],
        array_shape=[1, 2048, 4096],
        instrument="vbi",
        file_schema="level0_spec214",
        **dict(additional_header)
    )
    headers = ds.generate_headers(required_only=True)
    for h in headers:
        assert h["NAXIS"] == 3
        assert h["NAXIS1"] == 4096
        assert h["NAXIS2"] == 2048
        assert h["NAXIS3"] == 1
        assert h["INSTRUME"] == "VBI"

        for k in ("DATE-BEG", "PROP_ID"):
            assert k in h

        # Instrument required for VBI
        assert "VBI__001" in h.keys()
        assert "VBIFWHM" in h.keys()

        # TODO Actually rename the keys in the simulator
        assert h["DATE-BEG"] == h["DATE-OBS"]
        assert h["PROP_ID"] == h["ID___013"]
