import spiceypy as sp
from astropy.time import Time


def times2et(times, **kwargs):
    """ Convert time to ET (in SPICE format).

    Parameters
    ----------
    times : str, list
        Time values that will be passed to ``~astropy.time.Time`` function.

    **kwargs : dict
        Additional arguments for ``~astropy.time.Time`` function.

    Returns
    -------
    times : astropy.time.Time
        Time object.

    et : list
        List of ET (which means TDB in SPICE) values.
    """
    times = Time(times, **kwargs)
    return times, [sp.str2et(_t) for _t in times.iso]
