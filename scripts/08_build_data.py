"""Pack everything the page needs into one compact JSON (viz/data.json).

Nothing is computed here that the page shows as a statistic: rates, national sums
and figure counts are worked out in the browser from cases and population.
"""
import json
import re

import pandas as pd

from common import DATA, RAW, STATES
from project import geometry_paths, state_paths  # Albers USA, reused from the BirthRate project

Y0, Y1 = 1929, 2025
UNIT = 50  # one figure = this many reported cases per 100,000 residents in a year

# The five shown. Order is fixed: it sets the color and the drawing order of every tile.
DISEASES = [
    {"k": "measles", "name": "Measles", "color": "#e34948", "vax": "mmr"},
    {"k": "pertussis", "name": "Whooping cough", "color": "#2a78d6", "vax": "dtap"},
    {"k": "hepatitis_a", "name": "Hepatitis A", "color": "#008300", "vax": "hepa"},
    {"k": "mumps", "name": "Mumps", "color": "#eda100", "vax": "mmr"},
    {"k": "polio", "name": "Polio", "color": "#4a3aa7", "vax": "polio"},
]
VACCINES = {
    "mmr": "MMR vaccine, 1+ dose",
    "dtap": "DTaP vaccine, 4+ doses",
    "polio": "Polio vaccine, 3+ doses",
    "hepa": "Hepatitis A vaccine, 2+ doses",
}
SRC = {"tycho_weekly": "w", "tycho_cumulative": "c", "cdc_annual": "a", "cdc_weekly": "r"}

# Tile-grid position of each state: column, row.
GRID = {
    "AK": (0, 0), "ME": (10, 0),
    "WI": (5, 1), "VT": (9, 1), "NH": (10, 1),
    "WA": (0, 2), "ID": (1, 2), "MT": (2, 2), "ND": (3, 2), "MN": (4, 2), "IL": (5, 2), "MI": (6, 2), "NY": (8, 2), "MA": (9, 2),
    "OR": (0, 3), "NV": (1, 3), "WY": (2, 3), "SD": (3, 3), "IA": (4, 3), "IN": (5, 3), "OH": (6, 3), "PA": (7, 3), "NJ": (8, 3), "CT": (9, 3), "RI": (10, 3),
    "CA": (0, 4), "UT": (1, 4), "CO": (2, 4), "NE": (3, 4), "MO": (4, 4), "KY": (5, 4), "WV": (6, 4), "VA": (7, 4), "MD": (8, 4), "DE": (9, 4),
    "AZ": (1, 5), "NM": (2, 5), "KS": (3, 5), "AR": (4, 5), "TN": (5, 5), "NC": (6, 5), "SC": (7, 5), "DC": (8, 5),
    "OK": (3, 6), "LA": (4, 6), "MS": (5, 6), "AL": (6, 6), "GA": (7, 6),
    "HI": (0, 7), "TX": (3, 7), "FL": (8, 7),
}
assert set(GRID) == set(STATES) and len(set(GRID.values())) == 51


FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
        "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
        "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
        "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
        "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}


def shapes():
    """State outlines as SVG paths with their bounding boxes (us-atlas counties-10m, Census cartographic boundaries)."""
    topo = json.loads((RAW / "geo" / "counties-10m.json").read_text())
    out = {}
    for fips, d in state_paths(topo, precision=2).items():
        if fips not in FIPS:
            continue
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
        xs, ys = nums[0::2], nums[1::2]
        pad = 0.03 * max(max(xs) - min(xs), max(ys) - min(ys))
        out[FIPS[fips]] = {"d": d, "box": [round(min(xs) - pad, 2), round(min(ys) - pad, 2),
                                           round(max(xs) - min(xs) + 2 * pad, 2), round(max(ys) - min(ys) + 2 * pad, 2)]}
    assert set(out) == set(STATES), set(STATES) - set(out)
    names = {g["id"]: g["properties"]["name"] for g in topo["objects"]["counties"]["geometries"]}
    for fips, d in geometry_paths(topo, precision=2).items():
        if fips[:2] in FIPS:
            out[FIPS[fips[:2]]].setdefault("c", {})[fips] = [names[fips], d]
            nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
            xs, ys = nums[0::2], nums[1::2]   # middle of the bounding box, good enough to place a circle
            out[FIPS[fips[:2]]].setdefault("cc", {})[fips] = [round((min(xs) + max(xs)) / 2, 2), round((min(ys) + max(ys)) / 2, 2)]
    return out


def county():
    mmr = pd.read_csv(DATA / "county_mmr.csv", dtype={"fips": str})
    M = {}
    for r in mmr.itertuples():
        M.setdefault(r.fips, {})[int(r.year)] = r.pct
    cm = pd.read_csv(DATA / "county_measles.csv", dtype={"fips": str})
    cm = cm[cm.year.between(Y0, Y1)]
    K = {}
    for r in cm.itertuples():
        K.setdefault(r.fips, {})[int(r.year)] = int(r.cases)
    meta = pd.read_csv(DATA / "county_mmr_states.csv").fillna("")
    T = {r.st: {"years": r.years, "unit": r.unit.strip(), "age": r.age, "origin": r.origin, "n": int(r.county_rows)} for r in meta.itertuples()}
    return M, K, T


def main():
    years = list(range(Y0, Y1 + 1))
    idx = {y: i for i, y in enumerate(years)}
    n = len(years)

    pop = pd.read_csv(DATA / "state_population.csv")
    pop = pop[pop.st.isin(STATES) & pop.year.between(Y0, Y1)]
    P = {s: [None] * n for s in STATES}
    INC = {s: [None] * n for s in STATES}
    for r in pop.itertuples():
        P[r.st][idx[r.year]] = int(r.pop)
        INC[r.st][idx[r.year]] = None if pd.isna(r.pc_income) else int(r.pc_income)

    cases = pd.read_csv(DATA / "cases_state_year.csv")
    keys = [d["k"] for d in DISEASES]
    cases = cases[cases.disease.isin(keys) & cases.year.between(Y0, Y1)]
    assert not cases.duplicated(["disease", "st", "year"]).any()
    C = {k: {s: [None] * n for s in STATES} for k in keys}
    S = {k: {s: ["-"] * n for s in STATES} for k in keys}
    W = {k: {s: [0] * n for s in STATES} for k in keys}
    for r in cases.itertuples():
        i = idx[r.year]
        C[r.disease][r.st][i] = int(r.cases)
        code = SRC[r.source]
        if r.source == "cdc_weekly" and "provisional" in r.basis:
            code = "p"
        S[r.disease][r.st][i] = code.upper() if r.check else code
        if not pd.isna(r.weeks):
            W[r.disease][r.st][i] = int(r.weeks)
    S = {k: {s: "".join(v) for s, v in d.items()} for k, d in S.items()}
    W = {k: {s: v for s, v in d.items() if any(v)} for k, d in W.items()}

    vax = pd.read_csv(DATA / "vaccination.csv")
    vax = vax[vax.vaccine.isin(VACCINES) & vax.estimate.notna()]
    V = {}
    for r in vax.itertuples():
        row = [r.estimate, r.label]
        if r.series == "toddler":
            row += [r.lo, r.hi, int(r.n)]
        else:
            row += [None if pd.isna(r.pct_surveyed) else r.pct_surveyed, r.method if isinstance(r.method, str) else ""]
        V.setdefault(r.series, {}).setdefault(r.vaccine, {}).setdefault(r.st, {})[int(r.year)] = row

    ms = []
    for name in ("milestones_national.json", "milestones_pilot_states.json", "milestones_states.json"):
        p = DATA / name
        if p.exists():
            ms += json.loads(p.read_text())
    seen = set()
    for m in ms:
        key = (m["scope"], m["date"], m["headline"])
        assert key not in seen, f"duplicate milestone {key}"
        seen.add(key)
    ms.sort(key=lambda m: m["date"])

    cmmr, cmeasles, cmeta = county()
    out = {
        "shapes": shapes(), "cmmr": cmmr, "cmeasles": cmeasles, "cmeta": cmeta,
        "y0": Y0, "y1": Y1, "unit": UNIT, "diseases": DISEASES, "vaccines": VACCINES,
        "states": [{"k": s, "n": STATES[s], "c": GRID[s][0], "r": GRID[s][1]} for s in sorted(STATES)],
        "pop": P, "income": INC, "cases": C, "src": S, "weeks": W, "vax": V, "milestones": ms,
    }
    (DATA.parent / "viz" / "data.json").write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False))
    print("viz/data.json", (DATA.parent / "viz" / "data.json").stat().st_size, "bytes;", len(ms), "milestones")


if __name__ == "__main__":
    main()
