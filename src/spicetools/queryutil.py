import base64
from pathlib import Path
from urllib import request
import pandas as pd
import numpy as np
from io import StringIO

import requests

__all__ = ["SBDBQuery", "drop_impacted", "HorizonsSPKQuery", "download_jpl_de", "sanitize_comets"]

# impacted and permanently lost objects by 2024:
# see also https://en.wikipedia.org/wiki/Asteroid_impact_prediction#List_of_successfully_predicted_asteroid_impacts
IMPACTED = [
    # Asteroids
    "2008 TC3",  # On Earth at 2008-10-07T02:48:50.400+00:00
    "2014 AA",  # On Earth at 2014-01-02T02:30:35.086+00:00
    "2018 LA",  # On Earth at 2018-06-02T16:48:08.746+00:00
    "2019 MO",  # On Earth at 2019-06-22T21:29:24.866+00:00
    "2022 EB5",  # On Earth at 2022-03-11T21:25:49.509+00:00
    "2022 WJ1",  # On Earth at 2022-11-19T08:33:48.418+00:00
    "2023 CX1",  # On Earth at 2023-02-13T03:07:11.999+00:00
    "2024 BX1",  # On Earth at 2024-01-21T00:37:09.875+00:00
    "2024 RW1",  # On Earth at 2024-09-04T16:42:09.431+00:00
    "2024 UQ",  # On Earth at 2024-10-22T10:55:07.739+00:00
    # Comets
    "1981 V1",  # On Sun at 1981-11-04T12:45:12.615+00:00
    "1997 T2",  # On Sun at 1997-10-04T07:39:44.815+00:00
    "2002 X14",  # On Sun at 2002-12-12T07:10:55.815+00:00
    "1989 N3",  # On Sun at 1989-07-08T18:30:44.615+00:00
    "2003 K9",  # On Sun at 2003-05-24T20:51:43.816+00:00
    "2003 L8",  # On Sun at 2003-06-16T02:08:31.815+00:00
    "2003 M1",  # On Sun at 2003-06-16T15:06:07.815+00:00
    "2003 M2",  # On Sun at 2003-06-18T21:34:55.815+00:00
    "2003 M3",  # On Sun at 2003-06-18T09:20:31.816+00:00
    "2001 M8",  # On Sun at 2001-06-27T12:56:31.816+00:00
    "2008 C7",  # On Sun at 2008-02-09T21:34:54.815+00:00
    "2007 M5",  # On Sun at 2007-06-25T12:42:06.815+00:00
    "2007 V4",  # On Sun at 2007-11-03T19:32:30.815+00:00
    "2008 D9",  # On Sun at 2008-03-01T02:43:04.416+00:00
    "2008 H3",  # On Sun at 2008-04-17T06:27:42.816+00:00
    "2007 X10",  # On Sun at 2007-12-14T10:46:54.816+00:00
    "2008 J14",  # On Sun at 2008-05-14T09:34:54.815+00:00
    "2005 L7",  # On Sun at 2005-06-07T08:51:43.816+00:00
    "2005 L9",  # On Sun at 2005-06-07T09:49:19.816+00:00
    "2005 W16",  # On Sun at 2005-11-29T04:03:43.815+00:00
    "2005 L12",  # On Sun at 2005-06-12T16:32:31.815+00:00
    "2005 X5",  # On Sun at 2005-12-09T10:03:43.815+00:00
    "2004 Q6",  # On Sun at 2004-08-26T21:20:31.816+00:00
    "2007 E4",  # On Sun at 2007-03-03T11:30:06.816+00:00
    "2005 Y9",  # On Sun at 2005-12-27T17:58:55.815+00:00
    "2006 A5",  # On Sun at 2006-01-05T15:49:18.816+00:00
    "2006 X7",  # On Sun at 2006-12-12T17:30:06.816+00:00
]


def drop_impacted(df, desig_col="desig"):
    """Drop impacted objects from the DataFrame."""
    return df[~df[desig_col].isin(IMPACTED)].reset_index(drop=True)

# TODO: Eventually some of these may be moved to astroquery.jplsbdb


_SBDB_FIELDS = pd.read_csv(StringIO(
    """column,ignore,aonly,conly,simple,dtype
spkid,0,0,0,1,i
full_name,0,0,0,0,s
kind,0,0,0,0,s
pdes,0,0,0,1,s
name,0,0,0,0,s
prefix,0,0,1,1,s
neo,0,0,0,0,s
pha,0,1,0,0,s
sats,0,0,0,0,i
H,0,1,0,1,f
G,0,1,0,1,f
M1,0,0,1,1,f
M2,0,0,1,1,f
K1,0,0,1,1,f
K2,0,0,1,1,f
PC,0,0,1,1,f
S0,1,0,0,0,s
S0_sigma,1,0,0,0,s
diameter,1,0,0,0,f
extent,1,0,0,0,s
albedo,0,0,0,0,f
rot_per,0,0,0,0,f
pole,1,0,0,0,s
GM,1,0,0,0,f
density,1,0,0,0,f
BV,1,1,0,0,f
UB,1,1,0,0,f
IR,1,1,0,0,f
spec_B,0,1,0,0,s
spec_T,0,1,0,0,s
H_sigma,0,1,0,0,f
diameter_sigma,1,0,0,0,f
orbit_id,0,0,0,1,s
epoch,0,0,0,1,f
epoch_mjd,1,0,0,0,f
epoch_cal,1,0,0,0,s
equinox,1,0,0,0,s
e,0,0,0,1,f
a,0,0,0,0,f
q,0,0,0,1,f
i,0,0,0,1,f
om,0,0,0,1,f
w,0,0,0,1,f
ma,0,0,0,0,f
ad,0,0,0,0,f
n,1,0,0,0,f
tp,0,0,0,1,f
tp_cal,1,0,0,0,s
per,0,0,0,0,f
per_y,0,0,0,0,f
moid,0,0,0,0,f
moid_ld,1,0,0,0,f
moid_jup,0,0,0,0,f
t_jup,0,0,0,0,f
sigma_e,0,0,0,0,f
sigma_a,0,0,0,0,f
sigma_q,0,0,0,0,f
sigma_i,0,0,0,0,f
sigma_om,0,0,0,0,f
sigma_w,0,0,0,0,f
sigma_ma,0,0,0,0,f
sigma_ad,0,0,0,0,f
sigma_n,1,0,0,0,f
sigma_tp,0,0,0,0,f
sigma_per,0,0,0,0,f
class,0,0,0,1,s
source,0,0,0,0,s
soln_date,0,0,0,1,s
producer,1,0,0,0,s
data_arc,0,0,0,0,i
first_obs,0,0,0,0,s
last_obs,0,0,0,0,s
n_obs_used,0,0,0,0,i
n_del_obs_used,0,0,0,0,i
n_dop_obs_used,0,0,0,0,i
pe_used,0,0,0,0,s
sb_used,0,0,0,0,s
condition_code,0,0,0,0,s
rms,0,0,0,1,f
two_body,0,0,0,1,s
A1,0,0,0,1,f
A1_sigma,0,0,0,1,f
A2,0,0,0,1,f
A2_sigma,0,0,0,1,f
A3,0,0,0,1,f
A3_sigma,0,0,0,1,f
DT,0,0,0,1,f
DT_sigma,0,0,0,1,f"""),
    dtype={"column": str, "ignore": bool, "aonly": bool, "conly": bool, "simple": bool, "dtype": str}
)
_SBDB_FIELDS["dtype"] = _SBDB_FIELDS["dtype"].map({"i": int, "f": float, "s": str})
# For details of each column: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
# I found saving columns in, e.g., int32, does not really help reducing memory/storage usage for parquet.

SBDB_FIELDS = {}
for _name, _query in zip(["*", "all", "ignore", "simple", "simple_ast", "simple_com", "all_ast", "all_com"],
                         ["~ignore", "~ignore", "ignore", "simple", "simple & ~conly", "simple & ~aonly",
                          "~ignore & ~conly", "~ignore & ~aonly"]):
    _df = _SBDB_FIELDS.query(_query)
    SBDB_FIELDS[_name] = {c: t for c, t in zip(_df["column"], _df["dtype"])}


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

    # print(f"Downloaded {dename} to {output}")
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

            Some convenient options from ``SBDB_FIELDS`` are available ::

              * ``"*"``: Every available field.
              * ``"all"``: All fields except a few fields that are essentially
                empty for most (almost all) objects.
              * ``"simple"``: A few important fields for SPHEREx-SSO.
              * ``"all_[ast/com]"``: Selected for asteroids or comets.
              * ``"simple_[ast/com]"``: Selected for asteroids or comets.

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
                self.fields = list(SBDB_FIELDS[fields].keys())
                params["fields"] = ",".join(self.fields)
                if isinstance(fields, str):
                    if fields.endswith("ast"):
                        sb_kind = "a"
                    elif fields.endswith("com"):
                        sb_kind = "c"
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

    def query(self, output_parq=None, compression="gzip", sanitize_comet=False, col2kete=False, **kwargs):
        """Query SBDB and return the DataFrame.

        Parameters
        ----------
        output_parq : str, optional
            If provided, save the DataFrame to a parquet file.

        compression : str, optional
            Compression method to use in parquet file.

        sanitize_comet : bool, optional
            If `True`, sanitize the comets DataFrame by dropping objects ::

              * other than P/ or C/
              * with no magnitude information (likely unreliable comets or long dead)
              * with non-sensical solution date (likely very old records)
              * derived only by two-body physics (likely unreliable)

            Thus, the query should have had

        kwargs : dict, optional
            Additional keyword arguments to pass to `pd.DataFrame.to_parquet`.

        """
        response = requests.get(self.base_url, params=self._params)
        if not response.ok:
            raise ValueError(f"Query failed: {response.text}")

        data = response.json()
        if (ver := data["signature"]["version"]) != "1.0":
            raise ValueError(f"Only ver 1.0 is supported but got {ver}")

        try:
            self.df = pd.DataFrame(data["data"], columns=data["fields"])
            for c in self.df.columns:
                self.df[c] = self.df[c].astype(SBDB_FIELDS["*"][c])

        except Exception as e:
            raise ValueError(f"Failed to create DataFrame: {e}")

        if sanitize_comet:
            for col in ["prefix", "M1", "M2", "K1", "K2", "PC", "soln_date", "two_body"]:
                if col not in self.df.columns:
                    raise ValueError(f"Field `{col}` not in the query - cannot sanitize comets")

            self.df = sanitize_comets(self.df)

        if col2kete:
            self.df = self.df.rename(columns={
                "e": "ecc",
                "i": "incl",
                "q": "peri_dist",
                "w": "peri_arg",
                "tp": "peri_time",
                "om": "lon_node",
                "pdes": "desig",
            })

        if output_parq is not None:
            self.df.to_parquet(
                output_parq, compression=compression, index=False, **kwargs
            )

        return self.df


class HorizonsSPKQuery:
    """Class to handle JPL Horizons SPK queries."""

    def __init__(self, command, start=None, stop=None, obj_data=False, output=None):
        """ Get SPK query parameters for JPL Horizons.

        Parameters
        ----------
        command : str
            The ``COMMAND`` parameter in Horizons Query API. See the
            ``COMMAND`` Parameter section in this link for the details
            https://ssd-api.jpl.nasa.gov/doc/horizons.html#ephem_type
            For small bodies, it should generally be ending with a semicolon
            (``";"``), and in the format of one of these::
            - ``"<astnum>;"``, e.g., ``"99942;"``
            - ``"<name>;"`` (e.g., ``"Apophis;"``),
            - ``"DES=<des>;"`` (e.g., ``"DES=1999 AN10;"``).
            - ``"DES=<spkid>;"`` (e.g., ``"DES=20099942;"``).

        start, stop : str, optional
            Start and stop times of the query in ISO format. If not provided, the
            current time and one day later will be used (the default setting of
            Horizons API).

        obj_data : bool, optional
            If `True`, include object data in the SPK file.

        """
        self.base_url = "https://ssd.jpl.nasa.gov/api/horizons.api?format=json&EPHEM_TYPE=SPK"
        if not isinstance(command, str):
            raise TypeError("`command` must be str")

        self._params = {
            "COMMAND": f"'{command}'",
            "START_TIME": start,
            "STOP_TIME": stop,
            "OBJ_DATA": 'YES' if obj_data else 'NO'
        }

        self.output = output

    def query(self, decode=True):
        response = requests.get(self.base_url, params=self._params)
        self.url = response.url
        if not response.ok:
            raise ValueError(f"Query failed: {response.text}")

        data = response.json()
        if data["signature"]["version"] != "1.2":
            raise ValueError(f"Only ver 1.2 is supported but got {data['signature']['version']=}")

        # If the request was valid...
        try:
            self.spk = data["spk"]
            if not self.spk.startswith("REFGL1NQ"):
                raise ValueError("Invalid SPK data: It does not start with REFGL1NQ (DAF/SPK).")
            if decode:
                self.spk = base64.b64decode(self.spk)
        except KeyError:
            raise ValueError(f"The key 'spk' is not found in the response: {data}")

        if self.output is not None:
            with open(self.output, "wb" if decode else "w") as f:
                f.write(self.spk)
            # Logger.log(f"SPK data written to {self.output}")


def sanitize_comets(df_comet):
    """Sanitize the comets DataFrame."""
    # Drop objects
    # - other than P/ or C/
    # - with no magnitude information (likely unreliable comets or long dead)
    # - with non-sensical solution date (likely very old records)
    # - derived only by two-body physics (likely unreliable)
    _nanmags = pd.isna(df_comet[["M1", "M2", "K1", "K2", "PC"]].apply(pd.to_numeric, errors="coerce"))
    return df_comet.loc[
        (df_comet["prefix"].isin(["C", "P"]))
        & ~np.all(_nanmags, axis=1)
        & ~pd.isna(df_comet["soln_date"])
        & (df_comet["two_body"] != "T")
    ].copy().reset_index(drop=True)
