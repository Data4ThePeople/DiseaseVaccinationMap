"""Recompute every number cited in analysis/FINDINGS.md. Run from the project root.

Writes analysis/findings_numbers.txt. Nothing here is a model or a causal estimate:
each figure is a direct read of the source tables, side by side.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from common import NAME_TO_ABBR  # noqa: E402

pd.set_option("display.width", 200)
out = []
say = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731

# kindergarten coverage and exemptions by state (CDC SchoolVaxView); year = year the school year ends
k = pd.read_csv(ROOT / "data/raw/cdc/ijqb-a7ye.csv", dtype=str).fillna("")
k["st"] = k.Geography.str.upper().map(NAME_TO_ABBR)
k.loc[k.Geography == "United States", "st"] = "US"
k["y"] = k["School Year"].str[:4].astype(int) + 1
k["v"] = pd.to_numeric(k["Estimate (%)"], errors="coerce")
piv = lambda vac, dose=None: k[(k["Vaccine/Exemption"] == vac) & ((k.Dose == dose) if dose else True)].pivot_table(index="st", columns="y", values="v")  # noqa: E731
mmr, dtap, nonmed = piv("MMR"), piv("DTP, DTaP, or DT"), piv("Exemption", "Non-Medical Exemption")

cases = pd.read_csv(ROOT / "data/cases_state_year.csv")
rate = lambda d: cases[cases.disease == d].pivot_table(index="st", columns="year", values="rate")  # noqa: E731
count = lambda d: cases[cases.disease == d].pivot_table(index="st", columns="year", values="cases")  # noqa: E731

say("== 1. Kindergarten non-medical exemptions, selected states (percent of kindergartners)")
say(nonmed.loc[["US", "ID", "UT", "AZ", "OR", "WI"], [2010, 2015, 2020, 2025, 2026]].round(1).to_string())
say("\n== 1b. Kindergarten MMR coverage, selected states")
say(mmr.loc[["US", "ID", "UT", "AZ", "WI"], [2010, 2015, 2020, 2025, 2026]].round(1).to_string())

say("\n== 2. State MMR change 2019-20 to 2024-25 against 2025 measles rate (rank correlation, states with both years)")
t_all = pd.DataFrame({"mmr_chg": mmr[2025] - mmr[2020], "measles25": rate("measles")[2025]}).drop("US", errors="ignore")
t = t_all.dropna()
say(len(t), "states; Spearman", round(t.corr(method="spearman").iloc[0, 1], 2))
say("left out, no kindergarten MMR figure in one of the two years:", ", ".join(sorted(set(t_all.index) - set(t.index))))
loo = [t.drop(s).corr(method="spearman").iloc[0, 1] for s in t.index]
say("leaving out one state at a time, the correlation runs from", round(min(loo), 2), "to", round(max(loo), 2))

say("\n== 3. Whooping cough 2024 against each state's 2015-2019 average, with DTaP kindergarten change 2019-20 to 2023-24")
p = rate("pertussis")
w = pd.DataFrame({"dtap_chg": dtap[2024] - dtap[2020], "base": p[[2015, 2016, 2017, 2018, 2019]].mean(axis=1), "r2024": p[2024]})
w["pct_above_base"] = (w.r2024 / w.base - 1) * 100
w = w.dropna()
say(w.loc[["ID", "WI", "SD", "MN", "RI", "CT", "NY"]].round(1).to_string())
say(len(w), "states; Spearman dtap_chg vs pct_above_base", round(w[["dtap_chg", "pct_above_base"]].corr(method="spearman").iloc[0, 1], 2))
say("U.S. whooping cough cases 2023, 2024:", int(count("pertussis")[2023].sum()), int(count("pertussis")[2024].sum()))

say("\n== 4. Counties: kindergarten MMR (Johns Hopkins) and measles cases (Johns Hopkins tracker)")
cm = pd.read_csv(ROOT / "data/county_mmr.csv", dtype={"fips": str}).pivot_table(index=["fips", "st", "county"], columns="year", values="pct")
jm = pd.read_csv(ROOT / "data/raw/jhu/measles_county_all_updates.csv", dtype=str)
jm["fips"], jm["y"], jm["n"] = jm.location_id.str.zfill(5), jm.date.str[:4].astype(int), jm.value.astype(int)
say("tracker data through", jm.date.max())
cc = jm.pivot_table(index="fips", columns="y", values="n", aggfunc="sum", fill_value=0)
for f in ["04015", "49053", "45083", "48165", "42071", "12021", "53011", "27053", "55083"]:
    row = cm[cm.index.get_level_values(0) == f]
    name = row.index[0][2] + ", " + row.index[0][1]
    say(f"{name:18s} MMR by school year ending:", row.round(1).to_dict("records")[0],
        "| measles 2025:", int(cc.loc[f, 2025]) if f in cc.index else 0, "2026:", int(cc.loc[f, 2026]) if f in cc.index else 0)

say("\n== 5. Measles counts by state, outbreak years")
say(count("measles").loc[["CA", "WA", "NY", "MN", "OH", "TX", "UT", "AZ", "SC"], [2014, 2015, 2017, 2019, 2024, 2025]].fillna(-1).astype(int).to_string())

say("\n== 6. States that ended non-medical exemptions: kindergarten MMR before and after")
say(mmr.loc[["CA", "ME", "NY", "CT"], [2014, 2015, 2016, 2017, 2019, 2020, 2021, 2023, 2026]].round(1).to_string())

say("\n== 7. Mumps: reported cases in the U.S. (sum of states reporting) and leading states")
mu = count("mumps")
us = mu.sum()
say({y: int(us[y]) for y in [1968, 1975, 1985, 1986, 1987, 1988, 2005, 2006, 2016, 2017, 2019, 2025]})
for y in [1968, 1987, 2006, 2016, 2017]:
    top = cases[(cases.disease == "mumps") & (cases.year == y)].nlargest(4, "cases")
    say(y, list(zip(top.st, top.cases, top.rate.round(1))))

(ROOT / "analysis" / "findings_numbers.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))

usp = cases[cases.disease == "pertussis"].groupby("year").agg(c=("cases", "sum"), p=("pop", "sum"))
usp["r"] = usp.c / usp.p * 1e5
base = usp.loc[2015:2019, "r"].mean()
extra = f"U.S. whooping cough rate 2024 {usp.loc[2024, 'r']:.1f} per 100,000, {(usp.loc[2024, 'r'] / base - 1) * 100:.0f}% above the 2015-2019 average of {base:.1f}"
(ROOT / "analysis" / "findings_numbers.txt").write_text("\n".join(out + [extra]) + "\n")
print(extra)
