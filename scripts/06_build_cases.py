"""One row per disease, state and year, 1929 on, with the source of each number.

Order of preference for a disease-state-year:
  1. CDC final annual table (data/raw/bridge/annual_state_cases.csv), when present
  2. CDC weekly file, 2021 on (data/cdc_recent_state_year.csv)
  3. Project Tycho year-end running total, when it reaches week 50 or later
  4. Project Tycho sum of weekly reports, with the number of weeks reported

A state-year with no source has no row. It is "no data", never zero.

Output: data/cases_state_year.csv
"""
import pandas as pd

from common import DATA, NAME_TO_ABBR, RAW, STATES

FIRST_YEAR = 1929
BLOCKED = set()
DISEASES = ["measles", "pertussis", "mumps", "diphtheria", "hepatitis_a", "polio", "rubella", "smallpox", "varicella", "hepatitis_b"]


def tycho():
    t = pd.read_csv(DATA / "tycho_state_year.csv")
    t = t[t.st.isin(STATES) & (t.year >= FIRST_YEAR)].copy()
    full_cum = t.cum_last.notna() & (t.cum_week >= 50)
    t["cases"] = t.cum_last.where(full_cum, t.weekly_sum)
    t["source"] = pd.Series("tycho_weekly", index=t.index).where(~full_cum, "tycho_cumulative")
    t["basis"] = ("sum of " + t.weeks.astype("Int64").astype(str) + " weekly reports").where(
        ~full_cum, "year-end running total, week " + t.cum_week.astype("Int64").astype(str))
    t["weeks"] = t.weeks.where(~full_cum)
    # the two Tycho series disagree, or the running total fell during the year
    t["check"] = (full_cum & ((t.weekly_sum > 1.1 * t.cum_last + 5) | (t.cum_max > 1.25 * t.cum_last + 5))).astype(int)
    t = t[t.cases.notna()]
    return t[["disease", "st", "year", "cases", "source", "basis", "weeks", "check"]]


def cdc_recent():
    c = pd.read_csv(DATA / "cdc_recent_state_year.csv")
    c = c[c.cases.notna()].copy()
    c["source"], c["weeks"], c["check"] = "cdc_weekly", pd.NA, 0
    return c[["disease", "st", "year", "cases", "source", "basis", "weeks", "check"]]


def cdc_annual():
    p = RAW / "bridge" / "annual_state_cases.csv"
    if not p.exists():
        return None
    b = pd.read_csv(p, dtype=str)
    b["disease"] = b.disease.replace({"polio_paralytic": "polio"})
    b = b[b.disease.isin(DISEASES)].copy()
    b["st"] = b.state.str.upper().map(NAME_TO_ABBR)
    b["cases"] = pd.to_numeric(b.cases, errors="coerce")
    b = b[b.st.notna()]
    # New York 1968-1973: upstate did not report mumps, the table prints New York City. Show the City's
    # count, marked as City only (editor decision, October 6, 2026).
    part = b.cases.isna() & b.flag.fillna("").str.contains("other part=")
    b.loc[part, "cases"] = b.loc[part, "flag"].str.extract(r"other part=(\d+)")[0].astype(float)
    b["part"] = part
    # A final table that marks a state (NN not notifiable, N, U, NR, ...) is the last word for that year:
    # these rows block the provisional layers below and then drop out, so the page shows "no data".
    global BLOCKED
    BLOCKED = set(zip(b[b.cases.isna()].disease, b[b.cases.isna()].st, b[b.cases.isna()].year.astype(int)))
    b = b[b.cases.notna()]
    b["year"] = b.year.astype(int)
    assert not b.duplicated(["disease", "st", "year"]).any(), "duplicate rows in the annual table extract"
    b["source"] = b.part.map({True: "cdc_annual_part", False: "cdc_annual"})
    b["basis"] = b.part.map({True: "final annual table, New York City only", False: "final annual table"})
    b["weeks"], b["check"] = pd.NA, 0
    return b[["disease", "st", "year", "cases", "source", "basis", "weeks", "check"]]


if __name__ == "__main__":
    layers = [x for x in (cdc_annual(), cdc_recent(), tycho()) if x is not None]  # best first
    allrows = pd.concat(layers, ignore_index=True)
    out = allrows.drop_duplicates(["disease", "st", "year"], keep="first").copy()
    blocked = [k in BLOCKED for k in zip(out.disease, out.st, out.year)]
    print(sum(blocked), "provisional state-years dropped because the final table marks them")
    out = out[[not x for x in blocked]]
    assert not out.duplicated(["disease", "st", "year"]).any()
    pop = pd.read_csv(DATA / "state_population.csv")[["st", "year", "pop"]]
    out = out.merge(pop, how="left", on=["st", "year"])
    out["cases"] = out.cases.astype(int)
    out["rate"] = (out.cases / out["pop"] * 1e5).round(2)
    out = out.sort_values(["disease", "st", "year"])
    out.to_csv(DATA / "cases_state_year.csv", index=False)
    print(len(out), "rows")
    print(out.groupby(["disease", "source"]).agg(first=("year", "min"), last=("year", "max"), rows=("cases", "size"), cases=("cases", "sum")).to_string())
    print("\nreported cases 1929 on, all sources:")
    print(out.groupby("disease").cases.sum().sort_values(ascending=False).to_string())
    print("\nflagged for a look:", int(out.check.sum()))
