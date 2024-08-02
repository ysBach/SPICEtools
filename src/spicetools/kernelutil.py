import os


ROOTDIR = os.path.dirname(os.path.abspath(__file__))

META_TEMPLATE = (
    r"""
\begintext

    This meta file contains the paths to needed SPICE kernels.

\begindata
      PATH_VALUES     = ( '"""
    + os.path.dirname(os.path.abspath(__file__))
    + """/kernels/ ' )

      PATH_SYMBOLS    = ( 'KERNELS' )

KERNELS_TO_LOAD = (
    '{}'
)
"""
)


def make_meta(*args, output="kernel_meta"):
    """Create a kernel meta file from a list of kernel paths.

    Parameters
    ----------
    *args : str
        List of kernel paths. Some files that are avaliable within this package
        can be specified by using ``$KERNELS``. For example,
        ``"$KERNELS/lsk/naif0012.tls"``, ``"$KERNELS/pck/gm_de440.tpc"``,
        ``"$KERNELS/pck/pck00011.tpc"``.
    output : str, optional
        Name of the output kernel meta file.

    Returns
    -------
    None
    """
    contents = META_TEMPLATE.format("',\n    '".join(args))

    with open(output, "w") as f:
        f.write(contents)
