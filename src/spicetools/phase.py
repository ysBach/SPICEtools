import numpy as np
from .constants import D2R


__all__ = ['iau_hg_model']


def _hgphi12(alpha__deg):
    """Compute the phase function coefficients phi1 and phi2.

    Parameters
    ----------
    alpha__deg : float or np.ndarray
        Phase angle in degrees.
    """
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

    Parameters
    ----------
    alpha__deg : float or np.ndarray
        Phase angle in degrees.

    gpar : float
        The "slope" G parameter, typically between 0 and 1.
        Default is 0.15.

    Notes
    -----
    The widely used classical HG model for the phase function of asteroids is
    given by:
    Bowell, E., Hapke, B., Domingue, D., et al. (1989), "Application of
    photometric models to asteroids.", in Asteroids II, ed. R. P. Binzel, T.
    Gehrels, & M. S. Matthews, 524-556
    An additional discussion can be found in:
    Myhrvold, N. (2016), PASP, 128, 045004 (Sect. 2.2),

    """
    hgphi1, hgphi2 = _hgphi12(np.array(np.abs(alpha__deg)))
    # Just to avoid negative alpha error
    return (1 - gpar)*hgphi1 + gpar*hgphi2
