import ctypes

import numpy as np
import pytest
import spiceypy as sp

from spicetools.kernelutil import make_meta
from spicetools.timeutil import times2et

FILES = [
    "$KERNELS/lsk/naif0012.tls",
    "$KERNELS/pck/gm_de440.tpc",
    "$KERNELS/pck/pck00011.tpc",
]


@pytest.mark.parametrize(
    ("times", "et_expected", "etc_expected"),
    [
        ("2000-01-01T12:00:00",
         [64.18392728473108],
         [ctypes.c_double(64.18392728473108)]
         ),
        (["2000-01-01T12:00:00", "2030-01-01T12:00:00"],
         [64.18392728473108, 946771269.1839334],
         [ctypes.c_double(64.18392728473108), ctypes.c_double(946771269.1839334)]
         ),
    ]
)
def test_times2et(tmp_path, times, et_expected, etc_expected):
    mkpath = tmp_path/"test.mk"
    make_meta(*FILES, output=mkpath)
    _ = sp.furnsh(str(mkpath))

    # Without return_c
    times, et = times2et(times, return_c=False)
    np.testing.assert_array_almost_equal(et, et_expected)

    # With return_c
    times, et, etc = times2et(times, return_c=True)
    np.testing.assert_array_almost_equal(et, et_expected)
    for expected, actual in zip(etc_expected, etc):
        np.testing.assert_almost_equal(expected.value, actual.value)
