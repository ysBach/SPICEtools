import os
from pathlib import Path
import urllib


def download_jpl_de(dename="de440s", output=None):
    """Download JPL development ephemeris file

    Parameters
    ----------
    dename : str
        Name of the ephemeris file to download. Default is "de440s".
        See https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/ for available files.

    output : str, pathlib.Path, optional
        Name of the output file path. If not provided, it will be saved into
        this package's `kernels/` directory.
    """
    if not dename.endswith(".bsp"):
        dename += ".bsp"
    url = f"https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/{dename}"

    if output is None:
        # output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernels", dename)
        output = Path(__file__).parent / "kernels" / dename
    else:
        output = Path(output)

    # Download the file
    response = urllib.request.urlopen(url)
    with open(output, 'wb') as f:
        f.write(response.read())

    print(f"Downloaded {dename} to {output}")
    return output

