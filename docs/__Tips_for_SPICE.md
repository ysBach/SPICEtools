# CSPICE (SPICE toolkits)
As of 2023 early Nov., N0067 is the most recent version of SPICE toolkit.

To get a general idea, first few files of the [official tutorial](https://naif.jpl.nasa.gov/naif/tutorials.html) is highly recommended.

## Installation - Method 1 (Homebrew)
For Mac, the following installs CSPICE toolkits for N0067 to ``/opt/homebrew/bin`` (which are symlinks to binary executables in ``/opt/homebrew/Cellar/cspice/67``):

```
brew install cspice
```

But there are additional "applications" (=="executables"=="programs"=="utilities" under the SPICE lexicon) that should be downloaded separately:

```
cd /opt/homebrew/Cellar/cspice/67
wget -r --level 1 -np -nH -N --cut-dirs 6 -e robots=off --reject-regex '.\.ug|.\.txt' --reject 'brief,chronos,ckbrief,commnt,dskbrief,dskexp,frmdiff,inspekt,mkdsk,mkspk,msopck,simple,spacit,spkdiff,spkmerge,states,subpt,tictoc,tobin,toxfr,version' https://naif.jpl.nasa.gov/pub/naif/utilities/MacIntel_OSX_64bit/ -P bin/nontoolkitapps/
rm bin/nontoolkitapps/index.html*
chmod 755 -R bin/nontoolkitapps/
cd /opt/homebrew/bin && ln -s ../Cellar/cspice/67/bin/nontoolkitapps/* ./
```

**(OPTIONAL)** If you also want to download the "lessons":

```
cd /opt/homebrew/Cellar/cspice/67
wget -r --level 1 -np -nH -N --cut-dirs 6 -e robots=off https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/Lessons/spice_lessons_py_unix.zip
unzip -o spice_lessons_py_unix.zip -d share/cspice/doc/html/
rm spice_lessons_py_unix.zip
```

* It will overwrite the original ``index.html`` file to the one with lessons.
* To see the full manual, ``open /opt/homebrew/Cellar/cspice/67/share/cspice/doc/html/index.html``
* The files (kernels) required for each tutorial are at ``/opt/homebrew/Cellar/cspice/67/share/cspice/doc/html/lessons/**/kernels``


## Installation - Method 2 (manual)

You may download the main toolkit from [naif/toolkit](https://naif.jpl.nasa.gov/naif/toolkit.html) and the non-toolkit applications ("utilities") from [naif/utilities](https://naif.jpl.nasa.gov/naif/utilities.html).

Optionally, find the lesson from [``naif/toolkit_docs/Lessons`` directory](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/Lessons/). Then, unzip under ``cspice/doc/html/lessons`` (see ``toolkit_contents_<LANGUAGE>.html``/``Note About HTML Links``).

<details><summary><b>Using terminal</b> (click)</summary>
<p>

This is a specific example for the case of

* CSPICE (version N0067, the newest as of 2023 Oct)
* on Apple Silicon Mac
* with Python Lessons (optional).

On terminal (⚠️ the last ``wget`` line is **optional**, only if you want to download lesson files)

```
mkdir spice_c && cd spice_c
# Get the toolkit
wget -r --level 1 -np -nH -N --cut-dirs 6 -e robots=off https://naif.jpl.nasa.gov/pub/naif/toolkit/C/MacM1_OSX_clang_64bit/packages
# All utilities (including non-toolkit)
mkdir utils && cd utils && wget -r --level 1 -np -nH -N --cut-dirs 5 -e robots=off https://naif.jpl.nasa.gov/pub/naif/utilities/MacIntel_OSX_64bit/ && cd ..
# Lessons (optional)
wget -r --level 1 -np -nH -N --cut-dirs 6 -e robots=off https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/Lessons/spice_lessons_py_unix.zip
```

* Total ~40 MB for the toolkit, 79MB for utilities, and 24MB for the lessons.
  * The download speed was ~0.3MB/s for my case.
* See ``descriptn.txt`` for details.

Next steps:

```
chmod u+x importCSpice.csh && ./importCSpice.csh && rm cspice.tar
```

and done. (When you want to rebuild, ``cd cspice && ./makeall.csh && cd ..``)

If you downloaded lessons:

```
unzip -o spice_lessons_py_unix.zip -d cspice/doc/html/
```

To cleanup:

```
rm index.html*                # Unnecessary htmls from wget
rm utils/index.html*          # Unnecessary htmls from wget
rm packages                   # Unnecessary file from wget
rm importCSpice.csh           # Not necessary anymore
rm spice_lessons_py_unix.zip  # Not necessary anymore
```

The main file you will want to open is ``cspice/doc/html/index.html``:
```
open cspice/doc/html/index.html
```
You can start from ``Navigating Through the SPICE Components`` lesson to get an idea.

</p>
</details>






-----




## SPICE Kernels
A **kernel** is a "file" in SPICE lexicon. It includes
* Ephemeris kernel (usually ``.bsp``)
  * [JPL DE series](https://en.wikipedia.org/wiki/Jet_Propulsion_Laboratory_Development_Ephemeris) is probably the most useful ephemeris to use with SPICE. It contains the information of *major* objects (Sun, planets, Pluto, Moon). The information is calculated by considering the N-body interactions among all of them plus massive asteroids/KBOs.
    > ... numeric representations of positions, velocities and accelerations of major Solar System bodies, tabulated at equally spaced intervals of time, covering a specified span of years.[1] Barycentric rectangular coordinates of the Sun, eight major planets and Pluto, and geocentric coordinates of the Moon are tabulated. --- [Wikipedia](https://en.wikipedia.org/wiki/Jet_Propulsion_Laboratory_Development_Ephemeris)
  * Among them, for our purposes, the most recent version is DE440 series (2020; see [brief explanations](https://ssd.jpl.nasa.gov/planets/eph_export.html)). Among the [available files](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets), **DE440s** is enough since it covers 1849-2150 (see [``aa_summaries.txt`` file](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/aa_summaries.txt)).
  * Other objects: e.g., you may download the ephemeris of asteroids/comets and make binary ``*.bsp`` file via HORIZONS (see ``Example SPK Horizons Request`` at [here](https://ssd-api.jpl.nasa.gov/doc/horizons.html))
* Other generic kernels from [naif/generic_kernels](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/).
  * Including the leap-second kernel (e.g., ``lsk/naif0012.tls``) and physical constants kernel (e.g., ``/pck/gm_de440.tpc`` & ``pck/pck00011.tpc``), which are the most general kernels that will be used in almost any SPICE calculation for our purposes.
* Meta kernel: Normally a text file that contains the relative path to all necessary kernels that should be loaded for conducting a specific task (e.g., analyzing OSIRIS-REx data on 2020-01-01). Sometimes it is predefined by the mission team but many times the user has to specify files (kernels).

The extension that starts with the letter ``t`` (``.tls``, ``tpc``, etc)normally indicates it is a text file, rather than a binary (``b``, e.g., ``.bsp``).


## Useful SPICE Tools Notes (``spiceypy``)
All information:
* [spiceypy documentation](https://spiceypy.readthedocs.io/en/stable/documentation.html).
* CSPICE

Notation:
* **state vector**: length 6 vector (x, y, z, dx/dt, dy/dt, dz/dt).
* "**abcorr**": correction option available for light time (planetary aberration) and stellar aberration.

Functions in ``spiceypy`` (similar in ``CSPICE``):
* ``furnsh``: Load kernels (usually just meta kernel)
  * BSP files are generally loaded by `handle = spklef(filepath)` and unloaded by `spkuef(handle)`.
* ``bodvcd``: To extract double precision physical information of a body (e.g., $GM_\odot$ value)
  * ``bodvrd``: Identical but target name in `str`. ``bodvcd`` should use NAIF ID (`int`).
* ``str2et``: Convert string time (UTC scale) to ET (SPICE style formatted TDB).
  * ``et2utc`` or ``et2datetime`` can be used for inverse.
  * """Note: NAIF recommends the use of str2et_c instead of utc2et_c.""" ([link](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/utc2et_c.html))
* ``conics``: Returns the state vector from orbital elements, GM, and time. (inverse of ``oscelt``)
* ``oscelt``: Returns the orbital elements from state vector, GM, and time. (inverse of ``conics``)
  * ``oscltx``: Returns true anom., semi-major axis, orb. per. on top of ``oscelt``.
* ``spkez``: Returns the state vector of target w.r.t. an observer (relative position with abcorr).
  * Order: SPKEZP uses SPKAPO which uses SPKGPS.
  * The functions can be grouped like this:
  ```
             full state    only position
             ------------  -------------
    abcorr   int: spkez    int: spkezp
      yes    str: spkezr   str: spkpos

       no    int: spkgeo   int: spkgps  <-- used within "abcorr yes" functions above
  ```
  * int/str means object names should be given in NAIF ID (`int`) or `str`
  * So generally, ``spkez`` or ``spkezp`` could be used.
  * Note for position only VS state vector:
    > SPKPOS executes more quickly than SPKEZR when stellar aberration corrections are used
    >
    > SPICE Tutorial 18. SPK (ver. 2023 Apr)
  * Timing:
    ```
    %timeit sp.spkezp(int(spkid), TIMES_ET_CALC[0], "J2000", obs=3, abcorr="LT")
    %timeit sp.spkpos(spkid, TIMES_ET_CALC[0], "J2000", obs="EMB", abcorr="LT")
    %timeit sp.spkgps(int(spkid), TIMES_ET_CALC[0], "J2000", obs=3)
    5.75 µs ± 11.5 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    6.23 µs ± 14.9 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    3.91 µs ± 12.6 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

    %timeit sp.spkezp(int(spkid), TIMES_ET_CALC[0], "J2000", obs=399, abcorr="LT")
    %timeit sp.spkpos(spkid, TIMES_ET_CALC[0], "J2000", obs="EARTH", abcorr="LT")
    %timeit sp.spkgps(int(spkid), TIMES_ET_CALC[0], "J2000", obs=399)
    6.04 µs ± 9.95 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    6.55 µs ± 11.6 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    4.14 µs ± 23.7 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    ```
* ``gfpa``: Finds intervals where phase angle meets a certain criterion.
  * The term "Phase angle" in SPICE should rather be understood as "any angle made by 3 objects".
  * Unfortunately, `relate` can only be one of `<`, `=`, `>`, or absolute/local min/max.


```
handle = sp.spklef(f"{PATHS['ORBROOT']}/spkbsp/a/spk20000001.bsp")
%timeit sp.spkgps(20000001, ETS[0], ref="ECLIPJ2000", obs=399)
%timeit sp.spkezp(20000001, ETS[0], ref="ECLIPJ2000", abcorr="LT+S", obs=399)
%timeit sp.spkcvo("20000001", ETS[0], "ECLIPJ2000", "OBSERVER", "NONE", [0, 0, 0, 0, 0, 0], ETS[0], "399", "ECLIPJ2000")
sp.spkuef(handle)

4.42 μs ± 44.6 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
6.83 μs ± 274 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
7.67 μs ± 213 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
```