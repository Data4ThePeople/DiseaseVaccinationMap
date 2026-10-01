"""Turn Project Tycho weekly state rows into one row per disease, state and year.

Two series exist in the files and are kept apart (see DATASETS.md):
  weekly      counts for one week; the yearly figure is their sum, and the number
              of weeks present is carried beside it because absent weeks are not zeros
  cumulative  running totals from the start of the year; the yearly figure is the
              value at the latest week reported

Output: data/tycho_state_year.csv
"""
import zipfile

import numpy as np
import pandas as pd

from common import DATA, RAW

# disease key -> Tycho files. Files listed together are different names for the
# same disease in different years, never parts to be added (checked for overlap below).
FILES = {
    "measles": ["US.14189004"],
    "pertussis": ["US.27836007"],
    "mumps": ["US.36989005"],
    "diphtheria": ["US.397428000"],
    "hepatitis_a": ["US.40468003", "US.25102003"],
    "polio": ["US.398102009"],
    "rubella": ["US.36653000"],
    "smallpox": ["US.67924001"],
    "varicella": ["US.38907003"],
    "hepatitis_b": ["US.66071002", "US.76795007"],
}


def read(code):
    zf = zipfile.ZipFile(RAW / "tycho" / f"{code}.zip")
    name = next(n for n in zf.namelist() if n.endswith(".csv"))
    df = pd.read_csv(zf.open(name), dtype=str, keep_default_na=False)
    df = df[(df.Admin1ISO != "NA") & (df.Admin2Name == "NA") & (df.CityName == "NA")]
    df = df[(df.Fatalities == "0") & (df.AgeRange == "0-130") & (df.Subpopulation != "Military")]
    df = df.assign(
        st=df.Admin1ISO.str[-2:], n=df.CountValue.astype(int),
        start=pd.to_datetime(df.PeriodStartDate), end=pd.to_datetime(df.PeriodEndDate),
        cum=df.PartOfCumulativeCountSeries == "1", file=code,
    )
    return df[["st", "n", "start", "end", "cum", "file", "PlaceOfAcquisition", "DiagnosisCertainty", "SourceName"]]


def build(disease, codes):
    df = pd.concat([read(c) for c in codes], ignore_index=True)
    out = []

    wk = df[~df.cum].copy()
    wk["days"] = (wk.end - wk.start).dt.days + 1
    assert (wk.days == 7).all(), f"{disease}: non-weekly rows in the weekly series"
    wk["year"] = (wk.start + pd.Timedelta(days=3)).dt.year
    # Rows that split one week by place of acquisition or by file are added within
    # the week only if they are true parts. A second file for the same week is a
    # duplicate name for the same count, so take the larger, not the sum.
    per_file = wk.groupby(["st", "year", "start", "file"], as_index=False).n.sum()
    per_week = per_file.groupby(["st", "year", "start"], as_index=False).n.max()
    w = per_week.groupby(["st", "year"]).agg(weekly_sum=("n", "sum"), weeks=("start", "nunique")).reset_index()

    cu = df[df.cum].copy()
    # an MMWR year can start in the last days of December, so date the series a week in
    cu["year"] = (cu.start + pd.Timedelta(days=7)).dt.year
    cu["wk_end"] = np.ceil(((cu.end - cu.start).dt.days + 1) / 7).astype(int)
    per_file = cu.groupby(["st", "year", "end", "wk_end", "file"], as_index=False).n.sum()
    per_end = per_file.groupby(["st", "year", "end", "wk_end"], as_index=False).n.max()
    last = per_end.sort_values("end").groupby(["st", "year"]).tail(1)
    # a running total should never fall; the largest value seen guards against a late dip
    peak = per_end.groupby(["st", "year"]).n.max().rename("cum_max").reset_index()
    c = last.rename(columns={"n": "cum_last", "wk_end": "cum_week"})[["st", "year", "cum_last", "cum_week"]].merge(peak)

    m = w.merge(c, how="outer", on=["st", "year"])
    m.insert(0, "disease", disease)
    return m


if __name__ == "__main__":
    parts = [build(d, c) for d, c in FILES.items()]
    out = pd.concat(parts, ignore_index=True).sort_values(["disease", "st", "year"])
    assert not out.duplicated(["disease", "st", "year"]).any(), "duplicate disease-state-year"
    for col in ["weekly_sum", "weeks", "cum_last", "cum_week", "cum_max"]:
        out[col] = out[col].astype("Int64")
    out.to_csv(DATA / "tycho_state_year.csv", index=False)
    print(len(out), "rows")
    print(out.groupby("disease").agg(first=("year", "min"), last=("year", "max"), weekly=("weekly_sum", "sum"), cum=("cum_last", "sum")))
