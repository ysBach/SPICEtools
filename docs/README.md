This directory contains some notebooks and tips.

* [__Tips_for_SPICE.md](__Tips_for_SPICE.md): SPICE installation guide + Some tips for SPICE
* [00-SBDB_Query.ipynb](00-SBDB_Query.ipynb)\*: First step to download SBDB database (t_comp~10min)
    * The result of this notebook (ver of late 2023 Dec) is available from [my dropbox](https://www.dropbox.com/scl/fo/opi6k5b49bky6bomb6gmt/ACBDWV3cEECB2JH0X2GqAog?rlkey=injz3wl48ff7ci68djelbjkd6&dl=0) (2 files, total: 330MB).
* [01-astbsp_download.ipynb](01-astbsp_download.ipynb)\*: Download BSP for 1.3M objects (t_comp~1-2 weeks)
    * The result of this notebook (1.3 million BSP files covering early 2025 to late 2027) is available from [my dropbox](https://www.dropbox.com/scl/fi/9xr7hpxy7b8p1z856623a/spkbsp.zip?rlkey=ffnky4jq3qhw34tqqbylng4ep&dl=0) (you have to unzip it somewhere, .zip: 46GB, unzipped: 170GB).
* [02-CLUT.ipynb](02-CLUT.ipynb)\*: Calculate XYZ coordinate of all objects for the next year (timestep = 1 day) (t_comp ~ 1 h)
    * timespan & timestep can easily be tuned.
    * The result of this notebook (multiple parquet files) are available from [my dropbox](https://www.dropbox.com/scl/fo/juwwjqo7qkvjw3qom5nvo/AKgKYArR-bNhOMzl47qzr_Y?rlkey=57cixr681pk1io1l7fpp4g7ey&dl=0).
* [A1-TLUT.ipynb](A1-TLUT.ipynb): An appendix to show thermal flux look-up-table (TLUT) generation.
    * You never really need to look into it.
    * The result of this notebook is already included here (``abmags_neatm_T1_450_5um.csv``).
* [03-PLUT.ipynb](03-PLUT.ipynb): Calculate precise look-up-table (PLUT) for the next few days (t_comp ~ 1 h).
    * This should be run every time the next observation plan is updated.
* [04-FindSSO.ipynb](04-FindSSO.ipynb): Find SSO in the FoV (t_comp < 10 s)
    * This is the code intended to be run for every exposure


Notes:
* (\*: these are expected to be run roughly once/year cadence)
* (t_comp: single core computation time on MBP 14" [2021, macOS 13.6.4, M1Pro(6P+2E/G16c/N16c/32G)])