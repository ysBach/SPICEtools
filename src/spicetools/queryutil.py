import base64
import json
from pathlib import Path
from urllib import request

import requests

__all__ = ["download_jpl_de", "SBDBQuery", "horizons_spk_query_url", "horizons_spk_query"]


def _ordered_subtract(list1, list2):
    """Return a list with elements of list2 removed from list1, preserving order."""
    return [item for item in list1 if item not in list2]


SBDB_FIELDS = {
    "*": [
        # === object (Object Fields)
        "spkid"   ,  # object primary SPK-ID
        "full_name",  # object full name/designation
        "kind"    ,  # see below
        "pdes"    ,  # object primary designation
        "name"    ,  # object IAU name
        "prefix"  ,  # comet designation prefix
        "neo"     ,  # [Y/N] Near-Earth Object (NEO) flag
        "pha"     ,  # [Y/N] Potentially Hazardous Asteroid (PHA) flag
        "sats"    ,  # Number of known satellites
        # === phys_par (Physical Parameter Fields)
        "H"       ,  # absolute magnitude parameter
        "G"       ,  # magnitude slope parameter (default is 0.15)
        "M1"      ,  # comet total magnitude parameter
        "M2"      ,  # comet nuclear magnitude parameter
        "K1"      ,  # comet total magnitude slope parameter
        "K2"      ,  # comet nuclear magnitude slope parameter
        "PC"      ,  # comet nuclear magnitude law - phase coefficient
        "S0"      ,  # ??
        "S0_sigma",  # ??
        "diameter",  # [km] object diameter (from equivalent sphere)
        "extent"  ,  # [km] object bi/tri-axial ellipsoid dimensions
        "albedo"  ,  # geometric albedo
        "rot_per" ,  # [h] rotation period (synodic)
        "pole"    ,  # [deg] spin-pole direction in R.A./Dec.
        "GM"      ,  # [km^3/s^2] standard gravitational parameter
        "density" ,  # [g/cm^3] bulk density
        "BV"      ,  # color index B-V magnitude difference
        "UB"      ,  # color index U-B magnitude difference
        "IR"      ,  # color index I-R magnitude difference
        "spec_B"  ,  # [SMASSII] spectral taxonomic type
        "spec_T"  ,  # [Tholen] spectral taxonomic type
        "H_sigma" ,  # 1-sigma uncertainty in absolute magnitude H
        "diameter_sigma",  # [km] 1-sigma uncertainty in object diameter
        # === orbit (Orbit and Model Parameter Fields)
        "orbit_id",  # orbit solution ID
        "epoch"   ,  # [TDB] epoch of osculation in Julian day form
        "epoch_mjd",  # [TDB] epoch of osculation in modified Julian day form
        "epoch_cal",  # [TDB] epoch of osculation in calendar date/time form
        "equinox" ,  # equinox of reference frame
        "e"       ,  # eccentricity
        "a"       ,  # [au] semi-major axis
        "q"       ,  # [au] perihelion distance
        "i"       ,  # [deg] inclination; angle with respect to x-y ecliptic plane
        "om"      ,  # [deg] longitude of the ascending node
        "w"       ,  # [deg] argument of perihelion
        "ma"      ,  # [deg] mean anomaly
        "ad"      ,  # [au] aphelion distance
        "n"       ,  # [deg/d] mean motion
        "tp"      ,  # [TDB] time of perihelion passage
        "tp_cal"  ,  # [TDB] time of perihelion passage
        "per"     ,  # [d] sidereal orbital period
        "per_y"   ,  # [years] sidereal orbital period
        "moid"    ,  # [au] Earth Minimum Orbit Intersection Distance
        "moid_ld" ,  # [LD] Earth Minimum Orbit Intersection Distance
        "moid_jup",  # [au] Jupiter Minimum Orbit Intersection Distance
        "t_jup"   ,  # Jupiter Tisserand Invariant
        "sigma_e" ,  # eccentricity (1-sigma uncertainty)
        "sigma_a" ,  # [au] semi-major axis (1-sigma uncertainty)
        "sigma_q" ,  # [au] perihelion distance (1-sigma uncertainty)
        "sigma_i" ,  # [deg] inclination (1-sigma uncertainty)
        "sigma_om",  # [deg] long. of the asc. node (1-sigma uncertainty)
        "sigma_w" ,  # [deg] argument of perihelion (1-sigma uncertainty)
        "sigma_ma",  # [deg] mean anomaly (1-sigma uncertainty)
        "sigma_ad",  # [au] aphelion distance (1-sigma uncertainty)
        "sigma_n" ,  # [deg/d] mean motion (1-sigma uncertainty)
        "sigma_tp",  # [d] time of peri. passage (1-sigma uncertainty)
        "sigma_per",  # [d] sidereal orbital period (1-sigma uncertainty)
        "class"   ,  # orbit classification
        "source"  ,  # see below
        "soln_date",  # date/time of orbit determination (YYYY-MM-DD hh:mm:ss, Pacific Local)
        "producer",  # name of person (or institution) who computed the orbit
        "data_arc",  # [d] number of days spanned by the data-arc
        "first_obs",  # [UT] date of first observation used in the orbit fit
        "last_obs",  # [UT] date of last observation used in the orbit fit
        "n_obs_used",  # number of observations (all types) used in fit
        "n_del_obs_used",  # number of delay-radar observations used in fit
        "n_dop_obs_used",  # number of Doppler-radar observations used in fit
        "pe_used" ,  # JPL internal ID of the planetary ephemeris used in the OD
        "sb_used" ,  # JPL internal ID of the small-body ephemeris used in the OD
        "condition_code",  # orbit condition code (MPC 'U' parameter)
        "rms"     ,  # [arcsec] normalized RMS of orbit fit
        "two_body",  # [T/F] 2-body dynamics used flag
        "A1"      ,  # non-grav. radial parameter
        "A1_sigma",  # non-grav. radial parameter (1-sigma uncertainty)
        "A2"      ,  # non-grav. transverse parameter
        "A2_sigma",  # non-grav. transverse parameter (1-sigma uncertainty)
        "A3"      ,  # non-grav. normal parameter
        "A3_sigma",  # non-grav. normal parameter (1-sigma uncertainty)
        "DT"      ,  # [d] non-grav. peri.-maximum offset
        "DT_sigma",  # [d] non-grav. peri.-maximum offset (1-sigma uncertainty)
    ],
    # "kind" : indicates whether asteroid (a) or comet (c) and whether numbered (n)
    # or unnumbered (u); for example a value of an indicates a numbered asteroid
    # and cu indicates an unnumbered comet
    # "source": code indicating the source of the orbit: ORB=”JPL orbit
    # file”, MPC:mpn=”MPC numbered asteroid orbit file”, MPC:mpu=”MPC
    # unnumbered asteroid orbit file”, MPC:mp1=”MPC single opposition
    # short-arc orbit file”
    "ignore": ["S0", "S0_sigma", "diameter", "diameter_sigma", "extent", "pole", "GM",
               "density", "BV", "UB", "IR", "equinox", "epoch_mjd", "epoch_cal", "n",
               "sigma_n", "tp_cal", "moid_ld", "producer"],
    "aonly": ["H", "G", "pha", "BV", "UB", "IR", "spec_B", "spec_T", "H_sigma"],
    "conly": ["prefix", "M1", "M2", "K1", "K2", "PC"],
}
SBDB_FIELDS["all"] = _ordered_subtract(SBDB_FIELDS["*"], SBDB_FIELDS["ignore"])
SBDB_FIELDS["all_ast"] = _ordered_subtract(SBDB_FIELDS["all"], SBDB_FIELDS["conly"])
SBDB_FIELDS["all_com"] = _ordered_subtract(SBDB_FIELDS["all"], SBDB_FIELDS["aonly"])
SBDB_FIELDS_STR = {k: ",".join(v) for k, v in SBDB_FIELDS.items()}


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

    Returns
    -------
    output : pathlib.Path
        Path to the downloaded or existing ephemeris file.

    existed : bool
        `True` if the file already existed, `False` if it was downloaded.
    """
    if not dename.endswith(".bsp"):
        dename += ".bsp"

    if output is None:
        # output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernels", dename)
        output = Path(__file__).parent / "kernels" / dename
    else:
        output = Path(output)

    if output.exists() and not overwrite:
        return output, True

    # Download the file
    url = f"https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/{dename}"
    response = request.urlopen(url)

    with open(output, 'wb') as f:
        f.write(response.read())

    print(f"Downloaded {dename} to {output}")
    return output, False


class SBDBQuery:
    """Class to handle SBDB queries.
    It is based on SBDB Query API Version 1.0 (Aug 2021), which is the most
    recent version as of 2024 Sept.
    TODO: When this class gets mature enough, consider adding it to astroquery.
    """

    def __init__(self, info=None, fields="spkid", sort=None, limit=None, limit_from=None,
                 full_prec=False, sb_ns=None, sb_kind=None, sb_group=None, sb_class=None,
                 sb_sat=None, sb_xfrag=None, sb_defs=None, sb_cdata=None):
        """ Get SBDB query URL for small bodies.

        Parameters
        ----------
        info : {"count", "field", "all"}, optional
            When ``"count"`` is selected, return the number of objects
            available in the SBDB. When ``"field"`` is selected, return all
            available output fields. If ``"all"`` is selected, output count and
            field results. See mode ``I`` section in the link below for
            details.
            https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
            If provided, mode ``I`` will be used, and all other parameters
            except `sp_defs` will completely be ignored.
            Default is `None`.

        fields : str (comma-separated) or list of str, optional
            List of fields to be output. If no fields are specified, only the
            count (number of records matching found) is output. Field names are
            **case-sensitive**.
            Four convenient options are available: ``"all"``, ``"*"``,
            ``"all_ast"``, and ``"all_com"`` for all fields without a few
            fields that are essentially empty, literally all fields, and fields
            related to asteroids and comets, respectively. They are available
            via `spicetools.SBDB_FIELDS` in `list` type and
            `spicetools.SBDB_FIELDS_STR` in comma-separated `str` type.
            More specifically, ``"all"`` is ``"*"`` minus
            ``spicetools.SBDB_FIELDS["ignore"]``. ``"all_ast"`` is ``"all"``
            minus ``spicetools.SBDB_FIELDS["conly"]``. ``"all_com"`` is
            ``"all"`` minus ``spicetools.SBDB_FIELDS["aonly"]``.
            Default is ``"spkid"``.

        sort : str, optional
            Sort results by the specified field(s). Up to three fields can be
            specified, separated by commas (``,``) and descending direction can
            be specified by prefixing the field name with minus (``-``)
            (ascending is the default).

        limit : int, optional
            Limit data to the first `limit` results (where `limit` is the
            specified number and must be an integer value greater than zero).
            Default is `100`, so if you want all results, set `limit` to
            `None`.


        limit_from : int, optional
            Limit data starting from the specified record (where zero is the
            first record). Useful for “paging” through large datasets. Requires
            `limit`. **CAUTION**: it is possible for the underlying database to
            change between API calls.

        full_prec : bool, int optional
            Output data in full precision (normally, data are returned in
            reduced precision for display purposes). Default is `False`.

        sb_ns : str, optional
            Numbered status: restrict query results to either numbered
            (``"n"``) or unnumbered (``"u"``) small-bodies.

        sb_kind : str, optional
            Limit results to either asteroids-only (``"a"``) or comets-only
            (``"c"``).

        sb_group : str, optional
            Limit results to NEOs-only (``"neo"``) or PHAs-only (``"pha"``).

        sb_class : str (comma-separated) or list of str, optional
            Limit results to small-bodies with orbits of the specified class
            (or classes). Allowable values are valid 3-character orbit-class
            codes (see section below on orbit classes). If specifying more than
            one class, separate entities with a comma (e.g., ``"TJN,CEN"``) or
            provide a list of str (e.g., ``["TJN", "CEN"]``). **Codes are
            case-sensitive.**
            See "Available SBDB Orbit Classes" section at the link for details:
            https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html

        sb_sat : bool, optional
            Limit results to small-bodies with at least one known satellite.

        sb_xfrag : bool, optional
            Exclude all comet fragments (if any) from results.

        sb_defs : {"class", "field", "all"}, optional
            Return SBDB definitions and data related to available filter
            constraints. These data are typically only useful in supporting
            webpage apps. See "mode ``I``" section in the link for details.
            https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html
            If provided, mode ``I`` will be used, and all other parameters
            except `info` will completely be ignored.

        sb_cdata : str, optional
            Custom field constraints (``"sb-cdata"`` field). Maximum length is
            2048 characters when converted to the URI encoded string.
            See this link for details:
            https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html#constraints


        Notes
        -----
        This will get matured/generated in the future similar to
        `astroquery.jplsbdb`. This is at a primitive stage to query all
        information specifically for "all objects"
        """
        self.base_url = "https://ssd-api.jpl.nasa.gov/sbdb_query.api?"

        params = {}

        infomode = info is not None or sb_defs is not None

        if infomode:
            # Use info mode, ignore any other things
            if info not in ["count", "field", "all"]:
                raise ValueError("`info` must be 'count', 'field', or 'all'")
            if sb_defs not in ["class", "field", "all"]:
                raise ValueError("`sb_defs` must be 'class', 'field', or 'all'")
            params["info"] = info
            params["sb-defs"] = sb_defs

        else:
            try:
                self.fields = SBDB_FIELDS[fields]
                params["fields"] = SBDB_FIELDS_STR[fields]
            except KeyError:
                if not isinstance(fields, str):  # if list
                    try:
                        self.fields = fields
                        fields = ",".join(fields)
                    except TypeError:
                        raise TypeError(
                            f"`fields` must be str or list of str, got {type(fields)}"
                        )
                params["fields"] = fields
                self.fields = fields.split(",")

            if sort is not None:
                if not isinstance(sort, str):
                    raise TypeError("`sort` must be str")
                params["sort"] = sort

            if limit is not None:
                if not isinstance(limit, int):
                    raise TypeError("`limit` must be int")
                params["limit"] = limit

            if limit_from is not None:
                if not isinstance(limit_from, int):
                    raise TypeError("`limit_from` must be int")
                params["limit-from"] = limit_from

            if sb_ns is not None:
                if sb_ns not in ["n", "u"]:
                    raise ValueError("`sb_ns` must be 'n' or 'u'")
                params["sb-ns"] = sb_ns

            if sb_kind is not None:
                if sb_kind not in ["a", "c"]:
                    raise ValueError("`sb_kind` must be 'a' or 'c'")
                params["sb-kind"] = sb_kind

            if sb_group is not None:
                if sb_group not in ["neo", "pha"]:
                    raise ValueError("`sb_group` must be 'neo' or 'pha'")
                params["sb-group"] = sb_group

            if sb_class is not None:
                _allowed = ["IEO", "ATE", "APO", "AMO", "MCA", "IMB", "MBA", "OMB",
                            "TJN", "AST", "CEN", "TNO", "PAA", "HYA", "ETc", "JFc",
                            "JFC", "CTc", "HTC", "PAR", "HYP", "COM"]
                if isinstance(sb_class, str):
                    _classes = sb_class.split(",")
                else:
                    _classes = sb_class
                    sb_class = ",".join(sb_class)

                for _class in _classes:
                    if _class not in _allowed:
                        raise ValueError(f"The element {_class} in `sb_class` is not in {_allowed}.")

                params["sb-class"] = sb_class

            if sb_sat is not None:
                if not isinstance(sb_sat, bool):
                    raise TypeError("`sb_sat` must be bool")
                params["sb-sat"] = int(sb_sat)

            if sb_xfrag is not None:
                if not isinstance(sb_xfrag, bool):
                    raise TypeError("`sb_xfrag` must be bool")
                params["sb-xfrag"] = int(sb_xfrag)

            if sb_defs is not None:
                if not isinstance(sb_defs, str):
                    raise TypeError("`sb_defs` must be str")
                params["sb-defs"] = sb_defs

            if sb_cdata is not None:
                if not isinstance(sb_cdata, str):
                    raise TypeError("`sb_cdata` must be str")
                params["sb-cdata"] = sb_cdata

            params["full-prec"] = int(full_prec)

        self._params = params

    def query(self, convert_df=True):
        response = requests.get(self.base_url, params=self._params)
        if not response.ok:
            raise ValueError(f"Query failed: {response.text}")

        data = response.json()
        if (ver := data["signature"]["version"]) != "1.0":
            raise ValueError(f"Only ver 1.0 is supported but got {ver}")

        if convert_df:
            import pandas as pd
            self.df = pd.DataFrame(data["data"], columns=data["fields"])
            # reorder columns based on self.fields:
            # self.df = self.df[self.fields]
        else:
            self.fields = data["fields"]
            self.data = data["data"]
        # self.df = pd.DataFrame(self.data, columns=self.fields)

