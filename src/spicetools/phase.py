import numpy as np
from .constants import D2R


__all__ = ['iau_hg_model']


def _hgphi12(alpha__deg):
    alpha__rad = alpha__deg*D2R
    sin_a = np.sin(alpha__rad)
    f_a = sin_a/(0.119+1.341*sin_a-0.754*sin_a*sin_a)
    tan_a_half = np.tan(alpha__rad*0.5)
    w = np.exp(-90.56*tan_a_half*tan_a_half)
    phi1_s = 1 - 0.986*f_a
    phi2_s = 1 - 0.238*f_a
    phi1_l = np.exp(-3.332*tan_a_half**0.631)
    phi2_l = np.exp(-1.862*tan_a_half**1.218)
    return (w*phi1_s + (1-w)*phi1_l, w*phi2_s + (1-w)*phi2_l)


def iau_hg_model(alpha__deg, gpar=0.15):
    """The IAU HG phase function model in intensity (1 at alpha=0)
    """
    hgphi1, hgphi2 = _hgphi12(np.array(np.abs(alpha__deg)))
    # Just to avoid negative alpha error
    return (1 - gpar)*hgphi1 + gpar*hgphi2
