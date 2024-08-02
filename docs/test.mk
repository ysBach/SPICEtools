
\begintext

    This meta file contains the paths to needed SPICE kernels.

\begindata
      PATH_VALUES     = ( '/Users/ysbach/Dropbox/github/SPHEREx/SPICEtools/src/spicetools/kernels/ ' )

      PATH_SYMBOLS    = ( 'KERNELS' )

KERNELS_TO_LOAD = (
    '$KERNELS/lsk/naif0012.tls',
    '$KERNELS/pck/gm_de440.tpc',
    '$KERNELS/pck/pck00011.tpc',
    '$KERNELS/de432s.bsp'
)
