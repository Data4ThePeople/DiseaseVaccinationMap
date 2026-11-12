"""County figures for the state view.

  county MMR   Johns Hopkins county-level 2-dose MMR rates among kindergartners (Dong et al., JAMA 2025),
               school years 2017-18 to 2024-25. `year` is the calendar year the school year ends in.
               Rows without a county FIPS code (states that report by health region) are left out and counted.
  measles      Johns Hopkins measles tracker, lab-confirmed cases by county and report date, summed by calendar year.

Outputs: data/county_mmr.csv, data/county_measles.csv, data/county_mmr_states.csv
"""
import json

import pandas as pd

from common import DATA, RAW, STATES, download

BASE_MMR = "https://raw.githubusercontent.com/enshengdong/MMR_data/main/"
BASE_MEASLES = "https://raw.githubusercontent.com/CSSEGISandData/measles_data/main/"

if __name__ == "__main__":
    for f in ("mmr_data_us_counties_v2.csv", "mmr_data_sources_v2.csv"):
        download(BASE_MMR + f, RAW / "jhu" / f)
    download(BASE_MEASLES + "measles_county_all_updates.csv", RAW / "jhu" / "measles_county_all_updates.csv")

    m = pd.read_csv(RAW / "jhu" / "mmr_data_us_counties_v2.csv", dtype=str, encoding_errors="replace")
    cols = [c for c in m.columns if c.startswith("SY")]
    long = m.melt(id_vars=["FIPS", "County", "State"], value_vars=cols, var_name="sy", value_name="v")
    long["v"] = pd.to_numeric(long.v, errors="coerce")
    long = long[long.v.notna()]
    assert long.v.between(0, 1.0001).all(), "MMR rates expected as shares between 0 and 1"
    long["year"] = long.sy.str[2:6].astype(int) + 1
    long["pct"] = (long.v * 100).round(6)   # kept near full precision: the map picks its step and the page rounds once, from this
    regions = long[long.FIPS.isna()]
    long = long[long.FIPS.notna()].copy()
    long["fips"] = long.FIPS.str.replace(r"\.0$", "", regex=True).str.zfill(5)
    assert not long.duplicated(["fips", "year"]).any(), "duplicate county-year in the MMR file"
    assert long.State.isin(STATES).all()
    long.rename(columns={"State": "st", "County": "county"})[["fips", "st", "county", "year", "pct"]].to_csv(DATA / "county_mmr.csv", index=False)

    src = pd.read_csv(RAW / "jhu" / "mmr_data_sources_v2.csv", dtype=str, encoding_errors="replace")
    src = src.rename(columns={"Abbreviation": "st", "School Year(s) Available": "years", "Spatial Unit": "unit",
                              "Age Group": "age", "Data Origins": "origin", "Notes": "notes"})
    src["county_rows"] = src.st.map(long.groupby("State").size()).fillna(0).astype(int)
    src["region_rows"] = src.st.map(regions.groupby("State").size()).fillna(0).astype(int)
    src[["st", "years", "unit", "age", "origin", "notes", "county_rows", "region_rows"]].to_csv(DATA / "county_mmr_states.csv", index=False)

    c = pd.read_csv(RAW / "jhu" / "measles_county_all_updates.csv", dtype=str)
    assert set(c.outcome_type) == {"case_lab-confirmed"} and set(c.location_type) == {"county"}
    c["year"] = c.date.str[:4].astype(int)
    c["fips"] = c.location_id.fillna("00000").str.zfill(5)   # a row with no id is kept with the unknown-county rows, not dropped
    c["location_name"] = c.location_name.fillna("unknown")
    # rows that are not one county ("Unknown County, X" and health regions such as "Region 1, Louisiana") are filed
    # under their state's own key, 00 + state code, taken from the state named in the row: the tracker gives
    # some of them a real county's code (Oklahoma, Louisiana Region 1) or another state's code (Maryland's carries 23,
    # which is Maine's). They are never drawn as a county; 08_build_data.py places the health regions listed in
    # data/regions.json at the middle of their counties and counts the rest as not placed.
    geo = json.loads((RAW / "geo" / "counties-10m.json").read_text())   # state names and codes from the map's own geography
    name_fips = {g["properties"]["name"]: g["id"] for g in geo["objects"]["states"]["geometries"]}
    # a row is not one county when the tracker says so by name, or gives it no county code (0, or only the state's
    # two digits, as for Utah's health districts and Iowa's HHS districts)
    whole = (c.location_name.str.startswith("Unknown County") | c.location_name.str.contains(r"\bRegion\b")
             | c.fips.str.startswith("000"))
    c.loc[whole, "fips"] = "000" + c.loc[whole, "location_name"].str.split(", ").str[-1].str.strip().map(name_fips)
    assert c.fips.notna().all(), "a row not tied to a county names no state the map knows"
    c["cases"] = c.value.astype(int)
    out = c.groupby(["fips", "location_name", "year"], as_index=False).cases.sum()
    out.to_csv(DATA / "county_measles.csv", index=False)
    (DATA / "county_measles_meta.json").write_text('{"through": "%s"}' % c.date.max())   # last report date in the tracker

    print("county MMR:", len(long), "county-years in", long.State.nunique(), "states;", len(regions), "region rows left out in", sorted(regions.State.unique()))
    print(long.groupby("year").agg(counties=("fips", "nunique"), states=("State", "nunique")))
    print(src.unit.value_counts(dropna=False).to_dict()); print(src.age.value_counts(dropna=False).to_dict()); print(src.origin.value_counts(dropna=False).to_dict())
    print("county measles by year:", out.groupby("year").cases.sum().to_dict(), "; through", c.date.max())
    print("fips not 5 digits or unknown:", out[~out.fips.str.fullmatch(r"\d{5}")].location_name.unique()[:10])
