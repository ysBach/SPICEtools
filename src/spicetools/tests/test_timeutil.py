import ctypes

import numpy as np
import pytest

from spicetools.timeutil import times2et
from spicetools.kernelutil import make_meta
import spiceypy as sp
import os

FILES = [
    "$KERNELS/lsk/naif0012.tls",
    "$KERNELS/pck/gm_de440.tpc",
    "$KERNELS/pck/pck00011.tpc",
]
TEST_META_FILE = "test_meta.mk"
make_meta(*FILES, output=TEST_META_FILE)
handle = sp.furnsh(TEST_META_FILE)


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
def test_times2et(times, et_expected, etc_expected):
    # Without return_c
    times, et = times2et(times, return_c=False)
    np.testing.assert_array_almost_equal(et, et_expected)

    # With return_c
    times, et, etc = times2et(times, return_c=True)
    np.testing.assert_array_almost_equal(et, et_expected)
    for expected, actual in zip(etc_expected, etc):
        np.testing.assert_almost_equal(expected.value, actual.value)


# delete the temporary meta kernel file after tests
os.remove(TEST_META_FILE)  # Clean up the test files
