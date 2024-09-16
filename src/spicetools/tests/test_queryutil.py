from pathlib import Path
from spicetools.queryutil import download_jpl_de
import spicetools as spt

import pytest


@pytest.mark.parametrize(
    "dename, expected_output",
    [
        ("de440s", Path(spt.__file__).parent / "kernels/de440s.bsp"),
    ]
)
def test_download_jpl_de(dename, expected_output):
    output_path = download_jpl_de(dename, overwrite=True)
    assert str(output_path) == str(expected_output)
    assert Path(output_path).exists()

    with open(output_path, 'rb') as ff:
        l0 = ff.readline()
        ff.readline()
        l2 = ff.readline()

    assert l0.startswith(b"DAF/SPK")
    assert l2.split(b"\x00\x00JPL planetary and lunar ephemeris ")[1].startswith(b"DE440")
