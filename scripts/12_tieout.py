"""Tie-out: recompute what the page shows from the raw files, by a path that does not use the build's own tables.

  A. Every case count in viz/data.json equals data/cases_state_year.csv (the packing step lost nothing).
  B. For CDC final-annual years, the page's national sum equals the U.S. row CDC printed in the same table.
  C. For Project Tycho years, a sample of state-years is re-read straight from the zip with separate code.
  D. For CDC weekly years, a sample is re-read straight from the weekly file.
  E. Rates: recomputed from the BEA population file for a sample.
  F. Vaccination: a sample of points re-read from the publisher files.

Writes data/TIEOUT.md and exits non-zero on any mismatch.
"""
import json
import sys
import zipfile

import pandas as pd

from common import DATA, RAW, ROOT, STATES

D = json.loads((ROOT / "viz" / "data.json").read_text())
Y0 = D["y0"]
SHOWN = [d["k"] for d in D["diseases"]]
lines, bad = ["# Tie-out", "", "Built by `scripts/12_tieout.py`. Every line below was recomputed from a raw file.", ""], 0


def page(d, st, y):
    return D["cases"][d][st][y - Y0]


def check(label, got, want):
    global bad
    ok = got == want
    bad += not ok
    lines.append(f"| {label} | {want} | {got} | {'ok' if ok else 'MISMATCH'} |")


# A
c = pd.read_csv(DATA / "cases_state_year.csv")
c = c[c.disease.isin(SHOWN) & c.year.between(Y0, D["y1"])]
n = sum(page(r.disease, r.st, r.year) != r.cases for r in c.itertuples())
filled = sum(v is not None for d in SHOWN for s in STATES for v in D["cases"][d][s])
lines += ["## A. Packed data against the case table", "",
          f"{len(c):,} state-years in the table, {filled:,} filled cells on the page, {n} differ.", ""]
bad += n + (filled != len(c))

# B
a = pd.read_csv(RAW / "bridge" / "annual_area_cases_all.csv", dtype=str)
bs = pd.read_csv(RAW / "bridge" / "annual_state_cases.csv", dtype=str)
us = a[a.area == "United States"].assign(disease=lambda x: x.disease.replace({"polio_paralytic": "polio"}))
us = us[us.disease.isin(SHOWN)]
lines += ["## B. National sum on the page against the U.S. row CDC printed", "",
          "Only years where every state on the page comes from the final annual table. The printed U.S. row is read from the "
          "table itself, with footnote marks stripped.", "", "| disease, year | CDC printed | page sum | |", "|---|---|---|---|"]
nb, gaps = 0, []
for r in us.itertuples():
    y = int(r.year)
    codes = {D["src"][r.disease][s][y - Y0].lower() for s in STATES}
    if codes - {"a", "-"} or pd.isna(r.cases):
        continue
    total = sum(v for s in STATES if (v := page(r.disease, s, y)) is not None)
    if "-" in codes:   # a state left blank by the table: the printed total still counts any part it gave
        rows = bs[(bs.year == r.year) & (bs.disease.replace({"polio_paralytic": "polio"}) == r.disease) & bs.flag.fillna("").str.contains("other part=")]
        part = sum(int(f.split("other part=")[1].split(";")[0]) for f in rows.flag)
        gaps.append(f"| {r.disease} {y} | {int(float(r.cases))} | {total} | {part} | {'ok' if total + part == int(float(r.cases)) else 'MISMATCH'} |")
        bad += total + part != int(float(r.cases))
        continue
    nb += 1
    if total != int(float(r.cases)) or y % 5 == 0 or y in (2019, 2023):
        check(f"{r.disease} {y}", total, int(float(r.cases)))
lines += ["", f"{nb} disease-years compared in all; the table lists every fifth year, 2019, 2023 and any mismatch.", "",
          "Years where the table gives one or more states no figure (NN, not notifiable there). Those states show as no data. "
          "In 1968 to 1973 upstate New York did not report mumps but the table prints New York City's count, which is in the "
          "U.S. total and not on the map; the page sum falls short by exactly that part:", "",
          "| disease, year | CDC printed | page sum | part not mapped | |", "|---|---|---|---|---|"] + gaps + [""]


# C
def tycho_weekly_sum(code, iso, year):
    zf = zipfile.ZipFile(RAW / "tycho" / f"{code}.zip")
    df = pd.read_csv(zf.open(next(x for x in zf.namelist() if x.endswith(".csv"))), dtype=str, keep_default_na=False)
    df = df[(df.Admin1ISO == iso) & (df.CityName == "NA") & (df.Admin2Name == "NA") & (df.Fatalities == "0")
            & (df.PartOfCumulativeCountSeries == "0") & (df.AgeRange == "0-130")]
    mid = pd.to_datetime(df.PeriodStartDate) + pd.Timedelta(days=3)
    return int(df[mid.dt.year == year].CountValue.astype(int).sum())


lines += ["## C. Project Tycho years, re-read from the zip", "", "| disease, state, year | from zip | page | |", "|---|---|---|---|"]
for d, code, st, y in [("measles", "US.14189004", "OH", 1941), ("measles", "US.14189004", "CA", 1958), ("measles", "US.14189004", "TX", 1934),
                       ("polio", "US.398102009", "NY", 1952), ("polio", "US.398102009", "MN", 1946), ("pertussis", "US.27836007", "PA", 1947),
                       ("hepatitis_a", "US.40468003", "CA", 1971), ("pertussis", "US.27836007", "OH", 1950)]:
    assert D["src"][d][st][y - Y0].lower() == "w", (d, st, y)
    check(f"{d} {st} {y}", page(d, st, y), tycho_weekly_sum(code, f"US-{st}", y))
lines.append("")

# D
w = pd.read_csv(RAW / "cdc" / "x9gk-5huc.csv", dtype=str,
                usecols=["Reporting Area", "Current MMWR Year", "MMWR WEEK", "Label", "Cumulative YTD Current MMWR Year", "Cumulative YTD Previous MMWR Year"])
w["area"] = w["Reporting Area"].str.upper()
lines += ["## D. CDC weekly years, re-read from the weekly file", "", "| disease, state, year | from file | page | |", "|---|---|---|---|"]
for d, labels, areas, st, y in [("pertussis", ["Pertussis"], ["OHIO"], "OH", 2024), ("measles", ["Measles, Indigenous", "Measles, Imported"], ["TEXAS"], "TX", 2025),
                                ("pertussis", ["Pertussis"], ["NEW YORK", "NEW YORK CITY"], "NY", 2024), ("mumps", ["Mumps"], ["CALIFORNIA"], "CA", 2025)]:
    x = w[w.Label.isin(labels) & w.area.isin(areas)]
    if y == 2024:   # counted a year later: the prior-year column in the last week of 2025
        x = x[(x["Current MMWR Year"] == "2025") & (x["MMWR WEEK"] == "53")]
        got = int(pd.to_numeric(x["Cumulative YTD Previous MMWR Year"]).fillna(0).sum())
    else:
        x = x[(x["Current MMWR Year"] == "2025") & (x["MMWR WEEK"] == "53")]
        got = int(pd.to_numeric(x["Cumulative YTD Current MMWR Year"]).fillna(0).sum())
    check(f"{d} {st} {y}", page(d, st, y), got)
lines.append("")

# E
bea = pd.read_csv(zipfile.ZipFile(RAW / "bea" / "SAINC.zip").open("SAINC1__ALL_AREAS_1929_2025.csv"), dtype=str, encoding="latin-1")
bea = bea[bea.LineCode == "2"]
lines += ["## E. Population and rate", "", "| state, year | BEA population | page population | |", "|---|---|---|---|"]
for st, y in [("OH", 1941), ("CA", 1958), ("TX", 2025), ("AK", 1950), ("NY", 1990)]:
    row = bea[bea.GeoName.str.replace("*", "", regex=False).str.strip() == STATES[st]]
    check(f"{st} {y}", D["pop"][st][y - Y0], int(row[str(y)].iloc[0]))
lines += ["", "Rates are computed in the browser as cases / population x 100,000 from these two numbers; nothing is stored.", ""]

# F
lines += ["## F. Vaccination points against publisher files", "", "| point | publisher | page | |", "|---|---|---|---|"]
k = pd.read_csv(RAW / "cdc" / "ijqb-a7ye.csv", dtype=str)
r = k[(k.Geography == "Ohio") & (k["Vaccine/Exemption"] == "MMR") & (k["School Year"] == "2024-25")]
check("kindergarten MMR, Ohio 2024-25", D["vax"]["kinder"]["mmr"]["OH"]["2025"][0], float(r["Estimate (%)"].iloc[0]))
t = pd.read_csv(RAW / "cdc" / "fhky-rtsk.csv", dtype=str)
r = t[(t.Geography == "Texas") & (t.Vaccine == "≥1 Dose MMR") & (t["Birth Year/Birth Cohort"] == "2020") & (t.Dimension == "24 Months")]
check("toddler MMR, Texas born 2020 (shown at 2022)", D["vax"]["toddler"]["mmr"]["TX"]["2022"][0], float(r["Estimate (%)"].iloc[0]))
s_ = pd.read_csv(RAW / "vax_history" / "nis_state_survey_year.csv")
r = s_[(s_.state == "California") & (s_.vaccine == "dtp_4") & (s_.year == 2003)]
check("survey DTP 4+, California 2003", D["vax"]["survey"]["dtap"]["CA"]["2003"][0], float(r.estimate.iloc[0]))
u = pd.read_csv(RAW / "vax_history" / "national_pre1995.csv")
r = u[(u.survey == "USIS") & (u.age_group == "1-4 years") & (u.vaccine == "polio_3") & (u.year == 1964)]
check("national polio 3+, 1964", D["vax"]["national"]["polio"]["US"]["1964"][0], float(r.estimate.iloc[0]))
lines.append("")

lines.insert(3, f"**Result: {'all checks passed' if not bad else str(bad) + ' MISMATCHES'}.**")
(DATA / "TIEOUT.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if bad else 0)
