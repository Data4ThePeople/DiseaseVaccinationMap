"""Yearly state counts for 2021 on from the CDC weekly file.

The weekly counts are provisional and keep growing for months after the year ends,
so for year Y we prefer the "previous year" running total printed in the last week
of Y+1 (what was known a year later). Where Y+1 is not finished we fall back to
Y's own last week and say so. New York City reports apart from the rest of New
York and is added to it.

Output: data/cdc_recent_state_year.csv
"""
import pandas as pd

from common import DATA, NAME_TO_ABBR, RAW

LABELS = {
    "Measles, Indigenous": "measles", "Measles, Imported": "measles",
    "Pertussis": "pertussis", "Mumps": "mumps", "Rubella": "rubella",
    "Hepatitis A, Confirmed": "hepatitis_a", "Hepatitis, A, acute": "hepatitis_a",
    "Poliomyelitis, paralytic": "polio",
}
COLS = {
    "Reporting Area": "area", "Current MMWR Year": "year", "MMWR WEEK": "week", "Label": "label",
    "Cumulative YTD Current MMWR Year": "cur", "Cumulative YTD Current MMWR Year, flag": "cur_flag",
    "Cumulative YTD Previous MMWR Year": "prev", "Cumulative YTD Previous MMWR Year, flag": "prev_flag",
}

if __name__ == "__main__":
    w = pd.read_csv(RAW / "cdc" / "x9gk-5huc.csv", dtype=str, usecols=list(COLS)).rename(columns=COLS)
    w = w[w.label.isin(LABELS)].copy()
    w["disease"] = w.label.map(LABELS)
    w["area"] = w.area.str.upper()
    w["st"] = w.area.map({**NAME_TO_ABBR, "NEW YORK CITY": "NY"})
    w = w[w.st.notna()]
    w[["year", "week"]] = w[["year", "week"]].astype(int)
    for c in ("cur", "prev"):
        w[c] = pd.to_numeric(w[c], errors="coerce")

    last_week = w.groupby("year").week.max()
    # The hepatitis A label changed from "acute" to "Confirmed" late in 2023 and both
    # appear for a few weeks that autumn. Only year-end weeks are used; they must carry one.
    hep = w[w.disease == "hepatitis_a"].groupby(["year", "week"]).label.nunique()
    assert all(hep[(y, wk)] == 1 for y, wk in last_week.items()), "both hepatitis A labels in a year-end week"
    rows = []
    for (disease, st), g in w.groupby(["disease", "st"]):
        for year in sorted(last_week.index):
            lw = last_week[year]
            if year == last_week.index.max():  # the current, unfinished year
                continue
            own = g[(g.year == year) & (g.week == lw)]
            nxt = g[(g.year == year + 1) & (g.week == last_week.get(year + 1, -1))]
            use_next = len(nxt) and last_week.get(year + 1, 0) >= 52
            src, col = (nxt, "prev") if use_next else (own, "cur")
            if not len(src):
                continue
            flags = set(src[col + "_flag"].dropna())
            # "-" is CDC's mark for no reported cases; N and U are not numbers
            if flags & {"N", "U", "NN", "NP", "NC"} and src[col].notna().sum() == 0:
                cases, flag = None, ",".join(sorted(flags - {"-"}))
            else:
                cases, flag = int(src[col].fillna(0).sum()), ""
            rows.append(dict(disease=disease, st=st, year=year, cases=cases, flag=flag,
                             basis=f"as of week {last_week[year + 1]} of {year + 1}" if use_next else f"provisional, week {lw} of {year}"))
        # 2021 exists only as the prior-year column of 2022
        first = min(last_week.index)
        src = g[(g.year == first) & (g.week == last_week[first])]
        if len(src):
            flags = set(src.prev_flag.dropna())
            if flags & {"N", "U", "NN", "NP", "NC"} and src.prev.notna().sum() == 0:
                cases, flag = None, ",".join(sorted(flags - {"-"}))
            else:
                cases, flag = int(src.prev.fillna(0).sum()), ""
            rows.append(dict(disease=disease, st=st, year=first - 1, cases=cases, flag=flag,
                             basis=f"as of week {last_week[first]} of {first}"))
    out = pd.DataFrame(rows).sort_values(["disease", "st", "year"])
    assert not out.duplicated(["disease", "st", "year"]).any()
    out["cases"] = out.cases.astype("Int64")
    out.to_csv(DATA / "cdc_recent_state_year.csv", index=False)
    print(out.pivot_table(index="disease", columns="year", values="cases", aggfunc="sum"))
    print(out.groupby(["year", "basis"]).size())
    print(out[out.flag != ""].groupby(["disease", "flag"]).size())
