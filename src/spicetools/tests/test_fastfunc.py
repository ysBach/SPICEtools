import ctypes
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import spiceypy as sp

from spicetools.fastfunc import spkcvo, spkgps
from spicetools.kernelutil import make_meta
from spicetools.queryutil import download_jpl_de

de_path, de_existed = download_jpl_de("de440s", overwrite=False)  # avoid redownloading

FILES = [
    "$KERNELS/lsk/naif0012.tls",
    "$KERNELS/pck/gm_de440.tpc",
    "$KERNELS/pck/pck00011.tpc",
    "$KERNELS/de440s.bsp",
    "$KERNELS/tests/spk3200_19991201-20010101_retrieved20240916.bsp"
]
TEST_META_FILE = "test_meta.mk"
SPEEDOFLIGHT = 299792458.0/1000  # km/s
make_meta(*FILES, output=TEST_META_FILE)
handle = sp.furnsh(TEST_META_FILE)
ET_2000VE = 6868864.185613286  # ET for 2000-03-21T12:00:00


@pytest.mark.parametrize("ref", ["J2000", "ECLIPJ2000"])
@pytest.mark.parametrize("obs", [399, 301, 10, 20003200])
@pytest.mark.parametrize("et", [0.0, 100, 10000, ET_2000VE])
def test_spkgps_0(ref, obs, et):
    """
    Test the spkgps function with/without dummy lt.
    Case where state should be all 0s because target == observer
    """
    # Define the inputs
    _targ = ctypes.c_int(obs)  # Target body == observer
    _et = ctypes.c_double(et)  # ET (SPICE time)

    # === using dummy lt
    fast_spkgps = spkgps(ref=ref, obs=obs, dummy_lt=True)

    # Call the function
    state = fast_spkgps(_targ, _et)

    # Check the output
    np.testing.assert_array_almost_equal(state, np.zeros(3))

    # === using lt
    fast_spkgps = spkgps(ref=ref, obs=obs, dummy_lt=False)

    # Call the function
    state, lt = fast_spkgps(_targ, _et)

    # Check the output
    np.testing.assert_array_almost_equal(state, np.zeros(3))
    np.testing.assert_almost_equal(lt, 0.0)


@pytest.mark.parametrize(
    ("ref", "obs", "targ", "et", "state_expected"),
    [
        ("J2000", 399, 10, 0.0,
         [2.64990337e+07, -1.32757417e+08, -5.75567185e+07]),
        ("J2000", 399, 10, ET_2000VE,
         [1.49011707e+08, 1.63629256e+06, 7.09652164e+05]),
        ("ECLIPJ2000", 399, 10, 0.0,
         [ 2.64990337e+07, -1.44697297e+08, 6.11149426e+02]),
        ("ECLIPJ2000", 399, 10, ET_2000VE,
         [1.49011707e+08, 1.78355250e+06, 2.13328441e+02]),
    ]
)
def test_spkgps_non0(ref, obs, targ, et, state_expected):
    """
    Test the spkgps function with/without dummy lt.
    Test cases are :
    - Sun viewed from Earth at J2000 (ET=0.0)
    - Sun viewed from Earth at 2000-03-21 (ET=ET_2000VE)
    all at two reference frames: J2000 and ECLIPJ2000.
    """
    # Define the inputs
    _target = ctypes.c_int(targ)  # Target body (Sun)
    _et = ctypes.c_double(et)

    # === using dummy lt
    fast_spkgps = spkgps(ref=ref, obs=obs, dummy_lt=True)

    # Call the function
    state = fast_spkgps(_target, _et)

    # Check the output
    # allow 10 km uncertainty (?)
    np.testing.assert_allclose(state, np.array(state_expected), rtol=1e-6, atol=10)

    # === using lt
    fast_spkgps = spkgps(ref=ref, obs=obs, dummy_lt=False)

    # Call the function
    state, lt = fast_spkgps(_target, _et)

    # Check the output
    # allow 10 km uncertainty (?)
    np.testing.assert_allclose(state, np.array(state_expected), rtol=1e-6, atol=10)
    lt_expected = np.linalg.norm(state_expected) / SPEEDOFLIGHT
    np.testing.assert_almost_equal(lt, lt_expected, decimal=6)


@pytest.mark.parametrize("outref", ["J2000", "ECLIPJ2000"])
@pytest.mark.parametrize("refloc", ["OBSERVER", "TARGET"])
@pytest.mark.parametrize("abcorr", ["NONE", "LT", "LT+S", "CN", "CN+S"])
@pytest.mark.parametrize("obsctr", ["399", "10"])
@pytest.mark.parametrize("obsref", ["J2000", "ECLIPJ2000"])
@pytest.mark.parametrize("et", [0.0, 100, 10000, ET_2000VE])
def test_spkcvo_0(outref, refloc, abcorr, obsctr, obsref, et):
    """
    Test the spkcvo function with/without dummy lt.
    Case where state should be all 0s because target == observer
    """
    # Define the inputs
    _targ = sp.stypes.string_to_char_p(obsctr)
    obssta = sp.stypes.to_double_vector(np.zeros(6))
    _et = ctypes.c_double(et)

    # === using dummy lt
    spkcvo_boosted = spkcvo(outref, refloc, abcorr, obsctr, obsref, dummy_lt=True)

    state = spkcvo_boosted(_targ, obssta, _et)
    np.testing.assert_allclose(state, np.zeros(6), rtol=1e-5, atol=1e-5)

    # === using lt
    spkcvo_boosted = spkcvo(outref, refloc, abcorr, obsctr, obsref, dummy_lt=False)

    state, lt = spkcvo_boosted(_targ, obssta, _et)
    np.testing.assert_allclose(state, np.zeros(6), rtol=1e-5, atol=1e-5)
    np.testing.assert_almost_equal(lt, 0.0)


# Load the test cases for spkcvo
df_spkcvo_non0_cases = pd.read_csv(Path(__file__).parent / "spkcvo_test_cases.csv")
_spkcvo_sta = df_spkcvo_non0_cases[[f"sta{i}" for i in range(6)]].values
_spkcvo_obssta = df_spkcvo_non0_cases[[f"obssta{i}" for i in range(6)]].values


@pytest.mark.parametrize(
    ("outref", "refloc", "abcorr", "obsctr", "obsref", "et", "obssta", "state_expected"),
    zip(
        df_spkcvo_non0_cases["outref"].astype(str),
        df_spkcvo_non0_cases["refloc"].astype(str),
        df_spkcvo_non0_cases["abcorr"].astype(str),
        df_spkcvo_non0_cases["obsctr"].astype(str),
        df_spkcvo_non0_cases["obsref"].astype(str),
        df_spkcvo_non0_cases["et"],
        _spkcvo_obssta,
        _spkcvo_sta
    )
)
def test_spkcvo_non0(outref, refloc, abcorr, obsctr, obsref,
                     et, obssta, state_expected):
    """
    The test cases for spkcvo function with non-zero state.
    Generated by the following code::

        ```python
        import itertools
        import pandas as pd
        # print cases for spkcvo
        resdict = {k: [] for k in ["outref", "refloc", "abcorr", "obsctr", "obsref", "et", "lt"]}
        for _sta in ["obssta", "sta"]:
            for i in range(6):
                resdict[f"{_sta}{i}"] = []

        for outref, refloc, abcorr, obsctr, obsref, et, obssta in itertools.product(
            ["J2000", "ECLIPJ2000"],
            ["OBSERVER", "TARGET"],
            ["NONE", "LT", "LT+S", "CN", "CN+S"],
            ["399"],
            ["J2000", "ECLIPJ2000"],
            [0.0, ET_2000VE],
            [np.zeros(6), np.array([1, 2, 3, 4, 5, 6])]
        ):
            sta, lt = sp.spkcvo(
                target="20003200", et=et, outref=outref, refloc=refloc, abcorr=abcorr,
                obsctr=obsctr, obsref=obsref, obssta=obssta, obsepc=et
            )
            for k, v in zip("outref refloc abcorr obsctr obsref et lt".split(),
                            [outref, refloc, abcorr, obsctr, obsref, et, lt]):
                resdict[k].append(v)
            for i, v in enumerate(obssta):
                resdict[f"obssta{i}"].append(v)
            for i, v in enumerate(sta):
                resdict[f"sta{i}"].append(v)

        pd.DataFrame.from_dict(resdict).to_csv("spkcvo_test_cases.csv", index=False)
        ```
    """
    # Define the inputs
    _targ = sp.stypes.string_to_char_p("20003200")
    _et = ctypes.c_double(et)
    _obssta = sp.stypes.to_double_vector(np.array(obssta))

    # === using dummy lt
    spkcvo_boosted = spkcvo(outref, refloc, abcorr, obsctr, obsref, dummy_lt=True)
    state = spkcvo_boosted(_targ, _obssta, _et)

    # allow 1m & 1m/s uncertainties (?)
    np.testing.assert_allclose(state, state_expected, rtol=1e-5, atol=0.001)

    # === using lt
    spkcvo_boosted = spkcvo(outref, refloc, abcorr, obsctr, obsref, dummy_lt=False)
    state, lt = spkcvo_boosted(_targ, _obssta, _et)

    # allow 1m & 1m/s uncertainties (?)
    np.testing.assert_allclose(state, state_expected, rtol=1e-5, atol=0.001)
    lt_expected = np.linalg.norm(state_expected[:3]) / SPEEDOFLIGHT
    np.testing.assert_almost_equal(lt, lt_expected, decimal=6)


# delete the temporary meta kernel file after tests
os.remove(TEST_META_FILE)  # Clean up the test files
if not de_existed:
    # Clean if it is downloaded from this test
    os.remove(de_path)
