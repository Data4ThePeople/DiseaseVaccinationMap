"""BEA table SAINC1: state population (Census midyear estimates) and per-capita personal income, 1929 on.

Output: data/state_population.csv  (st, year, pop, pc_income)
Alaska and Hawaii have no figures before 1950; those cells stay empty.
"""
import zipfile

import pandas as pd

from common import DATA, NAME_TO_ABBR, RAW, download

if __name__ == "__main__":
    z = download("https://apps.bea.gov/regional/zip/SAINC.zip", RAW / "bea" / "SAINC.zip")
    zf = zipfile.ZipFile(z)
    name = next(n for n in zf.namelist() if n.startswith("SAINC1__ALL_AREAS"))
    df = pd.read_csv(zf.open(name), dtype=str, encoding="latin-1")
    df = df[df.LineCode.isin(["2", "3"])].copy()
    df["GeoName"] = df.GeoName.str.replace(r"\s*\*+$", "", regex=True).str.strip()
    df["st"] = df.GeoName.str.upper().map(NAME_TO_ABBR)
    df.loc[df.GeoName == "United States", "st"] = "US"
    df = df[df.st.notna()]
    years = [c for c in df.columns if c.isdigit()]
    long = df.melt(id_vars=["st", "LineCode"], value_vars=years, var_name="year", value_name="v")
    long["v"] = pd.to_numeric(long.v, errors="coerce")  # (NA) becomes empty
    wide = long.pivot(index=["st", "year"], columns="LineCode", values="v").reset_index()
    wide.columns = ["st", "year", "pop", "pc_income"]
    assert not wide.duplicated(["st", "year"]).any()
    assert wide.st.nunique() == 52, wide.st.nunique()
    wide = wide.dropna(subset=["pop"])
    wide["pop"] = wide["pop"].astype(int)
    wide.to_csv(DATA / "state_population.csv", index=False)
    print(len(wide), "rows", wide.year.min(), wide.year.max())
    print(wide[wide.st.isin(["US", "OH", "AK"])].groupby("st").agg(first=("year", "min"), last=("year", "max")))
