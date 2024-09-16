from pathlib import Path
from urllib import request


__all__ = ["download_jpl_de"]


def download_jpl_de(dename="de440s", output=None, overwrite=False):
    """Download JPL development ephemeris file (intended to be used one time).

    Parameters
    ----------
    dename : str
        Name of the ephemeris file to download. Default is "de440s".
        See https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/ for available files.

    output : str, pathlib.Path, optional
        Name of the output file path. If not provided, it will be saved into
        this package's `kernels/` directory.

    overwrite : bool, optional
        If `True`, overwrite the existing file if it exists. Default is
        `False`, i.e., not download any file but returns the path to the
        existing one.
    """
    if not dename.endswith(".bsp"):
        dename += ".bsp"

    if output is None:
        # output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernels", dename)
        output = Path(__file__).parent / "kernels" / dename
    else:
        output = Path(output)

    if output.exists() and not overwrite:
        return output

    # Download the file
    url = f"https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/{dename}"
    response = request.urlopen(url)

    with open(output, 'wb') as f:
        f.write(response.read())

    print(f"Downloaded {dename} to {output}")
    return output
