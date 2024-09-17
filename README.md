# SPICEtools
Python package to do simple SPICE calculations for space missions.

Originally developed for the SPHEREx mission, this tool calculates the precise location of all known solar system objects (SSOs) for the next several years, with an accuracy < 0.1 arcsec (assuming accurate orbital data). Internal tests confirmed that the original implementation of this method (by @ysBach), which uses SPICE toolkits with certain simplifying assumptions, can reproduce JPL Horizons calculations with a precision of ≲ 1 milli-arcsec for a few randomly selected asteroids observed from the WISE spacecraft (which is an expected accuracy for using SPICE). Additionally, the tool had to estimate crude fluxes for each object at any given time, aiding in the flagging of pixels and supporting other high-level sciences. The parts that were not specific for SPHEREx is decided to be located here. Therefore, this package is designed to be extensible for use with other missions.

Some tips & scripts are available in the `docs/` directory.

Important packages used in this repo:
* numpy, pandas, astropy, matplotlib, pyarrow
* spiceypy (MIT license)