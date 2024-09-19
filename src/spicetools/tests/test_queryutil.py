from pathlib import Path
from spicetools.queryutil import download_jpl_de, SBDBQuery, HorizonsSPKQuery

import pytest


@pytest.mark.parametrize(
    "dename",
    ["de440s"]
)
def test_download_jpl_de(tmp_path, dename):
    output_path, _ = download_jpl_de(dename, output=tmp_path / (dename + ".bsp"))
    assert isinstance(output_path, Path)
    assert output_path.name == dename + ".bsp"
    assert output_path.exists()

    with open(output_path, 'rb') as ff:
        l0 = ff.readline()
        ff.readline()
        l2 = ff.readline()

    assert l0.startswith(b"DAF/SPK")
    assert l2.split(b"\x00\x00JPL planetary and lunar ephemeris ")[1].startswith(b"DE440")


# Just a very simple test only
def test_SBDBQuery():
    sbdb = SBDBQuery(fields="spkid,pdes,", limit=3)
    sbdb.query()
    assert len(sbdb.df) == 3
    assert sbdb.df["spkid"].tolist() == [20000001, 20000002, 20000003]
    assert sbdb.df["pdes"].tolist() == ["1", "2", "3"]


@pytest.mark.parametrize("decode", [True, False])
@pytest.mark.parametrize(
    ("command", "start", "stop"),
    [
        ("1;", "2025-02-01", "2025-02-03"),
        ("Ceres;", "2025-02-01", "2025-02-03"),
        ("DES=1999 AN10;", "2025-02-01", "2025-02-03"),
        ("DES=20099942;", "2025-02-01", "2025-02-03"),
    ]
)
def test_HorizonsSPKQuery(tmp_path, command, start, stop, decode):
    output = tmp_path/"test.txt"
    spkq = HorizonsSPKQuery(command=command, start=start, stop=stop, output=output)
    spkq.query(decode=decode)
    assert output.exists()
