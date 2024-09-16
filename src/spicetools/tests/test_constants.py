import numpy as np

from spicetools import AU2KM, KM2AU, D2R, R2D
import pytest


@pytest.mark.parametrize(
    ('val', 'ans'),
    [(1, 57.29577951308232), (np.pi, 180), (0, 0)]
)
def test_r2d(val, ans):
    np.testing.assert_almost_equal(val * R2D, ans)


@pytest.mark.parametrize(
    ('val', 'ans'),
    [(1, 0.017453292519943295), (180, np.pi), (0, 0)]
)
def test_d2r(val, ans):
    np.testing.assert_almost_equal(val * D2R, ans)


@pytest.mark.parametrize(
    ('val', 'ans'),
    [(1, 149597870.700), (0, 0)]
)
def test_au2km(val, ans):
    np.testing.assert_almost_equal(val * AU2KM, ans)


@pytest.mark.parametrize(
    ('val', 'ans'),
    [(1, 6.684587122268445e-09), (149597870.700, 1), (0, 0)]
)
def test_km2au(val, ans):
    np.testing.assert_almost_equal(val * KM2AU, ans)
