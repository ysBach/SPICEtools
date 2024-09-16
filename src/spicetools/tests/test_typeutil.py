import numpy as np
import pytest
import spiceypy as sp

from spicetools.typeutil import empty_double_vector, str2char_p


@pytest.mark.parametrize(
    ('spkid', 'ans'),
    [(1, sp.stypes.string_to_char_p("1")),
     ("1", sp.stypes.string_to_char_p("1"))]
)
def test_str2char_p(spkid, ans):
    result = str2char_p(spkid)

    assert result.value == ans.value


@pytest.mark.parametrize(
    ('n', 'ans'),
    [(1, sp.stypes.empty_double_vector(1)),
     (2, sp.stypes.empty_double_vector(2))]
)
def test_empty_double_vector(n, ans):
    result = empty_double_vector(n)

    np.testing.assert_array_almost_equal(result, ans)
