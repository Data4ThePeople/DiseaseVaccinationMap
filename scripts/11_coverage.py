"""Source coverage check: how much of what the page shows is a direct, complete report.

For every disease and year: how many of the 51 areas have a figure, how many of those rest on
a full year of reports, how many on a partial year, and what share of the U.S. population lives
in the areas with a figure. Written to data/COVERAGE.md and data/coverage_by_year.csv.
"""
import pandas as pd

from common import DATA

SHOWN = ["measles", "pertussis", "hepatitis_a", "mumps", "polio"]
OTHERS = ["diphtheria", "rubella", "hepatitis_b"]


def kind(r):
    if r.source == "cdc_annual":
        return "final"
    if r.source == "cdc_weekly":
        return "provisional" if "provisional" in r.basis else "weekly, counted a year later"
    if r.source == "tycho_cumulative":
        return "year-end running total"
    return "weekly sum, 50+ weeks" if r.weeks >= 50 else "weekly sum, 40-49 weeks" if r.weeks >= 40 else "weekly sum, under 40 weeks"


if __name__ == "__main__":
    c = pd.read_csv(DATA / "cases_state_year.csv")
    c["kind"] = [kind(r) for r in c.itertuples()]
    pop = pd.read_csv(DATA / "state_population.csv")
    us = pop[pop.st == "US"].set_index("year")["pop"]
    c["us_pop"] = c.year.map(us)
    years = range(c.year.min(), c.year.max() + 1)

    rows = []
    for d in SHOWN + OTHERS:
        x = c[c.disease == d]
        for y in years:
            g = x[x.year == y]
            row = {"disease": d, "year": y, "areas": len(g), "pop_share": round(g["pop"].sum() / us[y] * 100, 1) if len(g) else 0.0,
                   "flagged": int(g.check.sum())}
            row.update(g.kind.value_counts().to_dict())
            rows.append(row)
    by = pd.DataFrame(rows).fillna(0)
    for col in by.columns[5:]:
        by[col] = by[col].astype(int)
    by.to_csv(DATA / "coverage_by_year.csv", index=False)

    kinds = [k for k in ["final", "weekly, counted a year later", "provisional", "year-end running total", "weekly sum, 50+ weeks",
                         "weekly sum, 40-49 weeks", "weekly sum, under 40 weeks"] if k in by.columns]
    lines = ["# Source coverage", "",
             "Built by `scripts/11_coverage.py` from `data/cases_state_year.csv`. Each cell counts state-years (51 areas a year).",
             "\"No figure\" means no source has a number for that state and year; the page shows it as \"no data\".", ""]
    for d in SHOWN + OTHERS:
        x = by[by.disease == d].copy()
        x["decade"] = (x.year // 10 * 10).astype(str) + "s"
        g = x.groupby("decade")
        t = g[kinds].sum()
        t.insert(0, "possible", g.size() * 51)
        t["no figure"] = t.possible - t[kinds].sum(axis=1)
        t["flagged"] = g.flagged.sum()
        t["avg pop share %"] = g.pop_share.mean().round(0).astype(int)
        gaps = x[x.areas == 0].year.tolist()
        runs, start = [], None
        for y in gaps + [None]:
            if start is None:
                start = prev = y
            elif y is not None and y == prev + 1:
                prev = y
            else:
                runs.append(f"{start}" if start == prev else f"{start} to {prev}")
                start = prev = y
        lines += [f"## {d}" + ("" if d in SHOWN else " (built, not shown)"), "",
                  "Years with no state figure at all: " + (", ".join(r for r in runs if r != "None") or "none") + ".", "",
                  "| decade | " + " | ".join(t.columns) + " |", "|---|" + "---|" * len(t.columns)]
        lines += ["| " + dec + " | " + " | ".join(str(v) for v in r) + " |" for dec, r in zip(t.index, t.values.tolist())]
        lines.append("")
    v = pd.read_csv(DATA / "vaccination.csv")
    v = v[v.estimate.notna() & (v.st != "US")]
    lines += ["## vaccination", "", "State-years with a figure, by series and vaccine:", "",
              "| series | vaccine | first year | last year | state-years |", "|---|---|---|---|---|"]
    for (s_, vk), g in v.groupby(["series", "vaccine"]):
        lines.append(f"| {s_} | {vk} | {g.year.min()} | {g.year.max()} | {len(g)} |")
    (DATA / "COVERAGE.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))
