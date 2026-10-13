"""BEA table SAINC1: state population (Census midyear estimates) and per-capita personal income, 1929 on.
Population for 1920 to 1928 comes from the Census Bureau's intercensal state estimates (st2029ts.txt,
July 1 estimates in thousands, released February 1996); BEA has nothing before 1929, so income is empty.

Output: data/state_population.csv  (st, year, pop, pc_income)
Alaska and Hawaii have no figures before 1950; those cells stay empty.
"""
import re
import zipfile

import pandas as pd

from common import DATA, NAME_TO_ABBR, RAW, download

CENSUS_1920S = "https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st2029ts.txt"


def census_1920s():
    """48 states, DC and the U.S., 1920 to 1928 (1929 is left to BEA, which prints the same Census estimate)."""
    f = download(CENSUS_1920S, RAW / "census_hist" / "st2029ts.txt")
    rows, years = [], []
    for line in open(f, encoding="latin-1"):
        t = line.split()
        if t and all(re.fullmatch(r"19\d\d", x) for x in t):
            years = [int(x) for x in t]
        elif years and len(t) == len(years) + 1 and (t[0] == "U.S." or re.fullmatch(r"[A-Z]{2}", t[0])):
            st = "US" if t[0] == "U.S." else t[0]
            rows += [(st, y, int(v.replace(",", "")) * 1000) for y, v in zip(years, t[1:]) if y < 1929]
    out = pd.DataFrame(rows, columns=["st", "year", "pop"])
    assert out.st.nunique() == 50 and len(out) == 50 * 9, (out.st.nunique(), len(out))
    out["pc_income"] = float("nan")
    return out


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
    wide["year"] = wide.year.astype(int)
    wide = pd.concat([census_1920s(), wide], ignore_index=True).sort_values(["st", "year"])
    assert not wide.duplicated(["st", "year"]).any()
    wide.to_csv(DATA / "state_population.csv", index=False)
    print(len(wide), "rows", wide.year.min(), wide.year.max())
    print(wide[wide.st.isin(["US", "OH", "AK"])].groupby("st").agg(first=("year", "min"), last=("year", "max")))
