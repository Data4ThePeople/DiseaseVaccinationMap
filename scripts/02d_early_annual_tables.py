"""State case counts for measles, whooping cough and polio, 1920 to 1955, from the federal annual tables.

Sources (scanned, CDC Stacks):
  1920-1950  Vital Statistics-Special Reports, Vol. 37, No. 9 (June 15, 1953), "Reported Incidence of
             Selected Notifiable Diseases: United States, Each Division and State, 1920-50"
             (record 84017): Table 15 acute poliomyelitis, Table 17 measles, Table 32 whooping cough
             (whooping cough from 1922).
  1951-1955  Annual supplements to the weekly morbidity report, "Reported Incidence of Notifiable
             Diseases in the United States", Table 3 (records 51624, 10892, 527, 671, 799).

The numbers were typed from the page images, not parsed: the scans' text layers are too damaged to
trust. Every cell as printed is in data/raw/bridge/early_readings.csv (year, disease, area, printed,
page). They were read twice, independently, and compared (see DATASETS.md). This script checks the
readings and writes them in the same layout as annual_state_cases.csv:

  - every state, division and U.S. cell must be present;
  - the states must add to each printed division row and the nine divisions to the printed U.S. row.
    A year and disease that fails is left out, unless the failure is listed in PRINTED_GAPS (the
    page itself does not add up; the cells are kept as printed).

Polio before 1956 is ALL reported polio (the 1920-50 table has no paralytic column, and the 1951-55
"Paralytic" column is incomplete because many states reported cases as "unspecified").

Output: data/raw/bridge/annual_state_cases_early.csv, data/raw/bridge/checks_early_sums.csv
"""
import os
import re
import sys

import pandas as pd

from common import RAW

BRIDGE = RAW / "bridge"
SRC = BRIDGE / "src"

RECORDS = {**{y: 84017 for y in range(1920, 1951)}, 1951: 51624, 1952: 10892, 1953: 527, 1954: 671, 1955: 799}
TABLE = {"polio": "Table 15, acute poliomyelitis", "measles": "Table 17, measles",
         "pertussis": "Table 32, whooping cough (pertussis)"}
COLUMN = {"polio": 'column "Poliomyelitis, acute: Total"', "measles": 'column "Measles"',
          "pertussis": 'column "Whooping cough"'}

DIVISIONS = {
    "New England": ["Maine", "New Hampshire", "Vermont", "Massachusetts", "Rhode Island", "Connecticut"],
    "Middle Atlantic": ["New York", "New Jersey", "Pennsylvania"],
    "East North Central": ["Ohio", "Indiana", "Illinois", "Michigan", "Wisconsin"],
    "West North Central": ["Minnesota", "Iowa", "Missouri", "North Dakota", "South Dakota", "Nebraska", "Kansas"],
    "South Atlantic": ["Delaware", "Maryland", "District of Columbia", "Virginia", "West Virginia",
                       "North Carolina", "South Carolina", "Georgia", "Florida"],
    "East South Central": ["Kentucky", "Tennessee", "Alabama", "Mississippi"],
    "West South Central": ["Arkansas", "Louisiana", "Oklahoma", "Texas"],
    "Mountain": ["Montana", "Idaho", "Wyoming", "Colorado", "New Mexico", "Arizona", "Utah", "Nevada"],
    "Pacific": ["Washington", "Oregon", "California"],
}
STATES = [s for d in DIVISIONS.values() for s in d]

# Rows where the printed page itself does not add up. Key: (year, disease, row); value: the printed
# total minus the sum of its printed parts. The cells are kept exactly as printed.
PRINTED_GAPS = {}

# Misprinted cells whose reading is an editor's decision rather than a plain read of the page.
# early_readings.csv keeps the cell as printed; the reading here is what is used, and the flag says so.
# Key: (year, disease, area) -> (printed, used, why)
EDITOR_READINGS = {
    (1932, "polio", "New York"): ("534", "334", 'printed "534", read as 334 by editor decision 2026-10-13: the Middle Atlantic '
                                  'row (1,806) and the U.S. row (3,820) add only with 334, and the weekly reports sum to 356'),
}

# Years left out on purpose, waiting for an editor's decision. Anything else that fails stops the build.
HELD = {}


def parse(printed):
    """-> (cases or None, flag). A dash is zero; dots mean no figure."""
    p = str(printed).strip()
    m = re.fullmatch(r"(\d[\d,]*)(\D.*)?", p)
    if m:
        mark = (m.group(2) or "").strip()
        return int(m.group(1).replace(",", "")), ("footnote mark " + mark.lstrip("^") if mark else "")
    if re.fullmatch(r"-(\^?\w)?", p):
        return 0, "-"
    return None, p


def url(rec):
    return "https://stacks.cdc.gov/view/cdc/%d/cdc_%d_DS1.pdf" % (rec, rec)


def main():
    r = pd.read_csv(BRIDGE / "early_readings.csv", dtype=str, keep_default_na=False)
    r["year"] = r.year.astype(int)
    assert not r.duplicated(["year", "disease", "area"]).any(), "a cell is entered twice"
    out, checks = [], []
    for (year, dis), g in r.groupby(["year", "disease"]):
        cell = dict(zip(g.area, g.printed))
        page = dict(zip(g.area, g.page))
        need = ["United States"] + list(DIVISIONS) + STATES
        missing = [a for a in need if a not in cell or "?" in cell[a]]
        for (y_, d_, a_), (printed, used, _) in EDITOR_READINGS.items():
            if (y_, d_) == (year, dis):
                assert cell[a_] == printed, "the printed cell changed: %s" % cell[a_]
                cell[a_] = used
        val = {a: parse(cell[a]) for a in cell}
        for (y_, d_, a_), (_, _, why) in EDITOR_READINGS.items():
            if (y_, d_) == (year, dis):
                val[a_] = (val[a_][0], why)
        for a, n in zip(g.area, g.note):   # a reading that needed the arithmetic says so in its flag
            if n:
                val[a] = (val[a][0], "; ".join(x for x in (val[a][1], n) if x))
        num = lambda a: val[a][0] or 0  # noqa: E731
        fails = []
        if not missing:
            for d, sts in DIVISIONS.items():
                gap = num(d) - sum(num(s) for s in sts)
                if gap != PRINTED_GAPS.get((year, dis, d), 0):
                    fails.append("%s off by %d" % (d, gap))
            gap = num("United States") - sum(num(d) for d in DIVISIONS)
            if gap != PRINTED_GAPS.get((year, dis, "United States"), 0):
                fails.append("United States off by %d" % gap)
        known = [k for k in PRINTED_GAPS if k[0] == year and k[1] == dis]
        ok = not missing and not fails
        checks.append({"year": year, "disease": dis, "us_printed": cell.get("United States", ""),
                       "sum_of_states": sum(num(s) for s in STATES if s in val),
                       "states_with_a_count": sum(1 for s in STATES if s in val and val[s][0] is not None),
                       "result": "kept" if ok else "held for an editor decision" if (year, dis) in HELD else "left out",
                       "why": "; ".join(([HELD[(year, dis)]] if (year, dis) in HELD else []) + (["missing or unreadable: " + ", ".join(missing)] if missing else []) + fails
                                        + ["page does not add, kept as printed: %s (printed total minus parts = %d)" % (k[2], PRINTED_GAPS[k]) for k in known])})
        if not ok:
            continue
        rec = RECORDS[year]
        for s in STATES:
            cases, flag = val[s]
            where = ("%s, PDF page %s, column %d" % (TABLE[dis], page[s], year) if year <= 1950
                     else "Table 3, reported cases by division and state, %d, PDF page %s, %s" % (year, page[s], COLUMN[dis]))
            out.append({"year": year, "state": s, "disease": dis, "cases": "" if cases is None else cases,
                        "flag": flag, "source_url": url(rec), "source_file": "stacks_%d_DS1.pdf" % rec,
                        "source_table": where + " (scan; typed from the page image)"})
    out = pd.DataFrame(out).sort_values(["year", "disease", "state"])
    out.to_csv(BRIDGE / "annual_state_cases_early.csv", index=False)
    ch = pd.DataFrame(checks).sort_values(["disease", "year"])
    ch.to_csv(BRIDGE / "checks_early_sums.csv", index=False)
    print(len(out), "state rows;", (ch.result == "kept").sum(), "of", len(ch), "disease-years kept")
    bad = ch[ch.result != "kept"]
    if len(bad):
        print(bad[["year", "disease", "why"]].to_string(index=False))
    unexpected = [(y, d) for y, d in zip(bad.year, bad.disease) if (y, d) not in HELD]
    return 1 if unexpected else 0


if __name__ == "__main__":
    sys.exit(main())
