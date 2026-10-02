"""State KPIs and party control for the state drill-down view.

Re-runnable: every source file is downloaded once into data/raw/kpi/src/ and
parsed from there. Nothing is typed in by hand.

Outputs (all under data/raw/kpi/):
  kpi_state_year.csv        series, variant, state, year, value, unit, flag, note, source_url, source_file
  party_control.csv         state, year, governor, senate, house, trifecta, as_of, flag, source, source_url
  party_control_overlap.csv Klarner and Ballotpedia side by side for the years both cover (1992-2011)
  party_control_ncsl_check.csv  the 2012-on rows checked against NCSL's dated tables for 2015-2021 and 2025

Rules followed here:
  - a publisher mark ((B), (D), (NA), --) goes in `flag` and the value stays empty
  - a year printed twice by the publisher (CPS redesign years) is kept twice,
    told apart by a suffix on `variant` and explained in `note`
  - shares computed here (BEA employment mix) say so in `note` with both inputs
See data/raw/kpi/NOTES.md for what each source is and where it breaks.
"""
import csv
import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from common import NAME_TO_ABBR, RAW, STATES, UA, download

KPI = RAW / "kpi"
SRC = KPI / "src"
SRC.mkdir(parents=True, exist_ok=True)

NUM = re.compile(r"^-?\d+(\.\d+)?$")
rows = []


def add(series, variant, state, year, value, unit, flag, note, url, file):
    rows.append(dict(series=series, variant=variant, state=state, year=int(year), value=value, unit=unit,
                     flag=flag, note=note, source_url=url, source_file=f"data/raw/kpi/src/{file}"))


def val(x):
    """(number or None, publisher mark or '') for one cell. Marks are never turned into numbers."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None, ""
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return None, ""
    t = s.replace(",", "") if re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", s) else s
    if NUM.match(t):
        f = float(t)
        return (int(f) if f.is_integer() and "." not in t else f), ""
    return None, s


def abbr(name):
    return NAME_TO_ABBR.get(re.sub(r"[.:*…]+", "", str(name)).strip().upper())


def year_label(label):
    """'2013 (38)' -> (2013, '38'); '2004 (revised)' -> (2004, 'revised'); '1999 8/' -> (1999, '8'); '2025(1)' -> (2025, '1')."""
    s = str(label).strip().rstrip(".").strip()
    m = re.match(r"^(\d{4})\s*(?:\(([^)]+)\)|(\d+)/|\s(\d+))?$", s)
    if not m:
        return None, None
    return int(m.group(1)), (m.group(2) or m.group(3) or m.group(4) or "")


def html_text(path):
    s = BeautifulSoup(Path(path).read_text(encoding="utf-8", errors="replace"), "lxml")
    for t in s(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t]+", " ", s.get_text("\n")))


def short(text, n=170):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 3].rstrip() + "..."


# ---------------------------------------------------------------- 1. median household income (CPS ASEC, H-8)
CPS_INC = "https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/h08.xlsx"
CPS_INC_FN = "https://www.census.gov/topics/income-poverty/income/guidance/cps-historic-footnotes.html"
# Years the publisher prints twice. The words come from the publisher's footnotes 38, 39 and 40.
INCOME_TWINS = {(2013, "38"): "2013_traditional_income_questions", (2013, "39"): "2013_redesigned_income_questions",
                (2017, ""): "2017_legacy_processing_system", (2017, "40"): "2017_updated_processing_system"}


def income_footnotes():
    t = html_text(download(CPS_INC_FN, SRC / "census_income_cps_historic_footnotes.html"))
    return {k: v.strip() for k, v in re.findall(r"\n(\d+)/\n([^\n]+)", t)}


def build_income():
    f = download(CPS_INC, SRC / "census_h08.xlsx")
    fn = income_footnotes()
    assert "38" in fn and "40" in fn, "income footnotes did not parse"
    d = pd.read_excel(f, header=None, dtype=str)
    panels = [i for i in range(len(d)) if re.fullmatch(r"(Current|\d{4}) Dollars", str(d.iat[i, 0]).strip())]
    assert len(panels) == 2, panels
    for p, start in enumerate(panels):
        label = str(d.iat[start, 0]).strip()
        base = "current_dollars" if label.startswith("Current") else f"{label[:4]}_dollars"
        end = panels[p + 1] if p + 1 < len(panels) else len(d)
        hdr = d.iloc[start + 1]
        cols = [(j, *year_label(hdr[j])) for j in range(1, d.shape[1]) if year_label(hdr[j])[0]]
        years = [y for _, y, _ in cols]
        for j, _, _ in cols:
            assert str(d.iat[start + 2, j]).startswith("Median") and str(d.iat[start + 2, j + 1]).startswith("Standard")
        for i in range(start + 3, end):
            st = abbr(d.iat[i, 0])
            if not st:
                continue
            for j, y, mark in cols:
                v, flag = val(d.iat[i, j])
                se, _ = val(d.iat[i, j + 1])
                variant, note = base, []
                if years.count(y) > 1:
                    variant = f"{base}__{INCOME_TWINS[(y, mark)]}"
                    note.append(f"publisher prints {y} twice; this is the row labelled '{str(hdr[j]).strip()}'")
                if mark:
                    note.append(f"fn {mark}: {short(fn.get(mark, 'Data have been revised to reflect a correction to the weights in the 2005 CPS ASEC.' if mark == 'revised' else ''))}")
                    flag = "; ".join(x for x in [flag, f"({mark})"] if x)
                if se is not None:
                    note.append(f"se={se}")
                if base != "current_dollars":
                    note.append("publisher's inflation adjustment: C-CPI-U 2000 on, R-CPI-U-RS before 2000")
                add("median_household_income", variant, st, y, v, "dollars", flag, "; ".join(note), CPS_INC, f.name)


# ---------------------------------------------------------------- 2. poverty rate (CPS ASEC, historical poverty table 19)
CPS_POV = "https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov19.xlsx"
CPS_POV_FN = "https://www.census.gov/topics/income-poverty/poverty/guidance/poverty-footnotes/cps-historic-footnotes.html"
POVERTY_TWINS = {(2013, "6"): "2013_traditional_income_questions", (2013, "5"): "2013_redesigned_income_questions",
                 (2017, ""): "2017_legacy_processing_system", (2017, "4"): "2017_updated_processing_system"}


def poverty_footnotes():
    t = html_text(download(CPS_POV_FN, SRC / "census_poverty_cps_historic_footnotes.html"))
    return {k: v.strip() for k, v in re.findall(r"\n(\d+)\. ([^\n]+)", t)}


def build_poverty():
    f = download(CPS_POV, SRC / "census_hstpov19.xlsx")
    fn = poverty_footnotes()
    assert "5" in fn and "6" in fn
    d = pd.read_excel(f, header=None, dtype=str)
    blocks = [(i, *year_label(d.iat[i, 0])) for i in range(len(d))
              if year_label(d.iat[i, 0])[0] and d.iloc[i, 1:].isna().all()]
    years = [y for _, y, _ in blocks]
    for b, (i0, y, mark) in enumerate(blocks):
        h = d.iloc[i0 + 1]
        assert str(h[4]).strip() == "Percent in poverty" and str(h[5]).startswith("Margin of error"), h.tolist()
        end = blocks[b + 1][0] if b + 1 < len(blocks) else len(d)
        for i in range(i0 + 2, end):
            st = abbr(d.iat[i, 0])
            if not st:
                continue
            v, flag = val(d.iat[i, 4])
            moe, _ = val(d.iat[i, 5])
            variant, note = "cps_asec", []
            if years.count(y) > 1:
                variant = f"cps_asec__{POVERTY_TWINS[(y, mark)]}"
                note.append(f"publisher prints {y} twice; this is the block labelled '{str(d.iat[i0, 0]).strip()}'")
            if mark:
                note.append(f"fn {mark}: {short(fn.get(mark, ''))}")
                flag = "; ".join(x for x in [flag, f"({mark})"] if x)
            if moe is not None:
                note.append(f"moe90={moe}")
            add("poverty_rate", variant, st, y, v, "percent", flag, "; ".join(note), CPS_POV, f.name)


# ---------------------------------------------------------------- 3. bachelor's degree or more, age 25+
DEC_EDU = "https://www2.census.gov/programs-surveys/decennial/2000/phc/phc-t-41/table06.csv"
ACS_DP02 = "https://api.census.gov/data/{y}/acs/acs1/profile"
ACS_YEARS = [y for y in range(2005, 2026) if y != 2020]


def census_key():
    sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
    from d4tp_env import get_key, load_env
    load_env()
    return get_key("CENSUS_API_KEY")


def get_json(url, dest, key=None):
    """Fetch JSON to dest once. The key is sent but never written or printed."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return json.loads(dest.read_text())
    req = urllib.request.Request(url + (f"&key={key}" if key else ""), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise RuntimeError(f"HTTP {e.code} for {url}") from None
    data = json.loads(body)
    dest.write_bytes(body)
    time.sleep(0.6)
    return data


def build_education():
    f = download(DEC_EDU, SRC / "census_phct41_table06.csv")
    text = f.read_text(encoding="latin-1")
    assert "Bachelor's Degree or Higher" in text and "BOTH SEXES" in text
    lines = list(csv.reader(io.StringIO(text)))
    hi = next(i for i, r in enumerate(lines) if r and r[0] == "Geographic area")
    years = [int(x) for x in lines[hi][1:] if x.strip().isdigit()]
    seen = set()
    for r in lines[hi + 1:]:
        if not r or not r[0].startswith(".."):
            continue
        st = abbr(r[0])
        if not st or st in seen:  # the file holds the both-sexes panel only; guard anyway
            continue
        seen.add(st)
        for y, cell in zip(years, r[1:]):
            v, flag = val(cell)
            note = "decennial census; 1950 to 2000 from the sample (long form), 1940 from the full count"
            if flag == "--":
                note = "publisher: not a state at that time"
            add("bachelors_or_higher_25plus", "decennial_census", st, y, v, "percent", flag, note, DEC_EDU, f.name)
    assert len(seen) == 51, len(seen)

    key = None
    for y in ACS_YEARS:
        base = ACS_DP02.format(y=y)
        vf = SRC / f"census_acs1_dp02_{y}_variables.json"
        df = SRC / f"census_acs1_dp02_{y}.json"
        if not (vf.exists() and df.exists()):
            key = key or census_key()
        meta = get_json(base + "/groups/DP02.json?", vf)
        if meta is None:
            print(f"  ACS 1-year {y}: not on the API, skipped")
            continue
        vs = meta["variables"]
        hits = sorted(k for k, m in vs.items() if re.fullmatch(r"DP02_\d{4}E", k)
                      and re.search(r"bachelor's degree or higher", m["label"], re.I)
                      and "EDUCATIONAL ATTAINMENT" in m["label"])
        assert len(hits) == 1, (y, hits)
        stem = hits[0][:-1]
        want = [stem + s for s in ("E", "M", "PE", "PM") if stem + s in vs]
        data = get_json(f"{base}?get=NAME,{','.join(want)}&for=state:*", df, key)
        head, body = data[0], data[1:]
        ix = {h: n for n, h in enumerate(head)}
        url = f"{base}?get=NAME,{','.join(want)}&for=state:*"
        for r in body:
            st = abbr(r[ix["NAME"]])
            if not st:
                continue
            # From 2018 the E cell is a count and PE the percent; before that E already holds the percent.
            pick = stem + "PE" if stem + "PE" in ix and vs[stem + "E"]["label"].lower().find("percent") < 0 else stem + "E"
            if stem + "PE" in ix and pick == stem + "E":
                e, _ = val(r[ix[stem + "E"]]); pe, _ = val(r[ix[stem + "PE"]])
                if e is None or e < 0 or e > 100:
                    pick = stem + "PE"
            v, flag = val(r[ix[pick]])
            mk = pick[:-1] + "M"
            moe, _ = val(r[ix[mk]]) if mk in ix else (None, "")
            if v is not None and v < -1000:  # Census API sentinel for an annotated cell
                flag, v = f"api annotation {v}", None
            assert v is None or 5 < v < 80, (y, st, pick, v)
            note = [f"ACS 1-year, table DP02, variable {pick}"]
            if moe is not None and moe >= 0:
                note.append(f"moe90={moe}")
            add("bachelors_or_higher_25plus", "acs_1yr", st, y, v, "percent", flag, "; ".join(note), url, df.name)


# ---------------------------------------------------------------- 4. people without health insurance
HI_BASE = "https://www2.census.gov/programs-surveys/demo/tables/health-insurance/time-series/"
HI_ORIG_FN = {"2": "Implementation of a new March CPS processing system.",
              "3": "Figures are revised to correct for nine omitted weights from the original March 1992 CPS file.",
              "4": "Implementation of Census 1990 based population controls.",
              "5": "Data collection method changed from paper and pencil to computer-assisted interviewing.",
              "6": "Health insurance questions were redesigned.",
              "7": "Beginning with the March 1998 CPS, people with no coverage other than access to Indian Health Service are no longer considered covered.",
              "8": "Estimates reflect the results of follow-up verification questions and of Census 2000 based population controls.",
              "9": "Implementation of a 28,000 household sample expansion.",
              "15": "These estimates from the 2005 ASEC were revised based on improvements to the algorithm that assigned coverage to dependents, and there was an adjustment to the weights."}
HI_AB_FN = {"2": HI_ORIG_FN["8"], "3": HI_ORIG_FN["9"], "4": HI_ORIG_FN["15"],
            "10": "footnote 10 is printed in the table but is not defined on the publisher's series page"}
HI_ORIG_TWINS = {(1999, ""): "1999_before_verification_questions", (1999, "8"): "1999_with_verification_questions_2000_controls",
                 (2004, ""): "2004_as_first_published", (2004, "15"): "2004_revised_2005_asec"}


def check_orig_footnotes(text):
    """The dictionary above is typed from the file's own footnote block; make sure the file still says so."""
    flat = re.sub(r"\s+", " ", text)
    for k, phrase in [("8", "follow-up verification questions"), ("9", "28,000 household sample expansion"),
                      ("15", "2005 ASEC were revised"), ("6", "Health insurance questions were redesigned"),
                      ("7", "Indian Health Service")]:
        assert re.search(rf"{k}/ [^/]*{re.escape(phrase)}", flat), k


def build_uninsured():
    # (a) original CPS series HI-4, 1987 to 2005, fixed-width text
    url = HI_BASE + "original/orghihistt4.txt"
    f = download(url, SRC / "census_orghihistt4.txt")
    text = f.read_text(encoding="latin-1")
    check_orig_footnotes(text)
    pages = re.split(r"(?=Table HI-4\.)", text)
    got = []
    for pg in pages:
        if "Not covered" not in pg[:900]:
            continue
        st, prev = None, ""
        for line in pg.splitlines():
            m = re.match(r"^ ([A-Z][A-Za-z .]+):\s*$", line)
            if m:
                # "District of" / "Columbia:" is printed on two lines
                st = abbr(f"{prev} {m.group(1)}" if prev == "District of" else m.group(1))
                assert st or m.group(1) == "United States", line
                continue
            prev = line.strip()
            m = re.match(r"^ (\d{4})(?: (\d+)/)?\.+\s+(.*)$", line)
            if m and st:
                tok = m.group(3).split()
                assert len(tok) == 9, line
                got.append((st, int(m.group(1)), m.group(2) or "", tok))
    per = {}
    for st, y, mark, tok in got:
        per.setdefault(st, []).append(y)
    for st, y, mark, tok in got:
        v, flag = val(tok[3])
        se, seflag = val(tok[4])
        variant, note = "cps_asec_original_HI4", []
        if per[st].count(y) > 1:
            variant += f"__{HI_ORIG_TWINS[(y, mark)]}"
            note.append(f"publisher prints {y} twice; this is the row labelled '{y}{' ' + mark + '/' if mark else ''}'")
        if mark:
            note.append(f"fn {mark}: {short(HI_ORIG_FN[mark])}")
            flag = "; ".join(x for x in [flag, f"({mark}/)"] if x)
        note.append(f"se={se}" if se is not None else f"se={seflag}")
        add("uninsured_rate", variant, st, y, v, "percent", flag, "; ".join(note), url, f.name)

    # (b) revised CPS series HIA-4 (1999 to 2009) and HIB-4 (1999 to 2012)
    for tag, path, fname in [("HIA4", "hia/hihistt4.xls", "census_hihistt4.xls"), ("HIB4", "hib/hihistt4b.xls", "census_hihistt4b.xls")]:
        url = HI_BASE + path
        f = download(url, SRC / fname)
        d = pd.read_excel(f, header=None, dtype=str)
        assert str(d.iat[3, 2]).strip() == "Not Covered" and str(d.iat[5, 4]).strip() == "Percent", (d.iat[3, 2], d.iat[5, 4])
        st = None
        for i in range(6, len(d)):
            lab = str(d.iat[i, 0]).strip()
            if lab.endswith(":") and not lab.startswith("FOOT"):
                st = abbr(lab)
                continue
            y, mark = year_label(lab)
            if not y or not st:
                continue
            v, flag = val(d.iat[i, 4])
            se, seflag = val(d.iat[i, 5])
            note = []
            if mark:
                note.append(f"fn {mark}: {short(HI_AB_FN[mark])}")
                flag = "; ".join(x for x in [flag, f"({mark})"] if x)
            note.append(f"se={se}" if se is not None else f"se={seflag}")
            add("uninsured_rate", f"cps_asec_{tag}", st, y, v, "percent", flag, "; ".join(note), url, f.name)

    # (c) ACS 1-year, table HIC-4_ACS, 2008 on
    url = HI_BASE + "acs/hic04_acs.xlsx"
    f = download(url, SRC / "census_hic04_acs.xlsx")
    d = pd.read_excel(f, header=None, dtype=str, engine="calamine")
    assert "Civilian noninstitutionalized" in str(d.iat[2, 0])
    cols = [(j, *year_label(d.iat[4, j])) for j in range(2, d.shape[1]) if year_label(d.iat[4, j])[0]]
    for j, _, _ in cols:
        assert str(d.iat[5, j + 2]).strip() == "Percent", d.iat[5, j + 2]
    for i in range(6, len(d)):
        st = abbr(d.iat[i, 0])
        if not st or str(d.iat[i, 1]).strip() != ".Uninsured":
            continue
        for j, y, mark in cols:
            v, flag = val(d.iat[i, j + 2])
            moe, _ = val(d.iat[i, j + 3])
            note = ["civilian noninstitutionalized population"]
            if mark:
                flag = "; ".join(x for x in [flag, f"({mark})"] if x)
            if moe is not None:
                note.append(f"moe90={moe}")
            add("uninsured_rate", "acs_1yr_HIC4", st, y, v, "percent", flag, "; ".join(note), url, f.name)


# ---------------------------------------------------------------- 5. employment mix (BEA SAEMP25)
# The table was discontinued on Sept. 27, 2024. BEA's archive copy is the March 2024 release.
BEA_URL = "https://apps.bea.gov/regional/histdata/releases/0324pistate/SAINC.zip"
BEA_LINES = {"SIC": {"total": "10", "farm": "70", "manufacturing": "400", "government": "900"},
             "NAICS": {"total": "10", "farm": "70", "manufacturing": "500", "government": "2000"}}
BEA_DESC = {"total": "Total employment", "farm": "Farm employment", "manufacturing": "Manufacturing",
            "government": "Government and government enterprises"}


def build_employment():
    f = download(BEA_URL, SRC / "bea_archive_0324pistate_SAINC.zip")
    zf = zipfile.ZipFile(f)
    for cls, table in [("SIC", "SAEMP25S"), ("NAICS", "SAEMP25N")]:
        name = next(n for n in zf.namelist() if n.startswith(table + "__ALL_AREAS"))
        d = pd.read_csv(zf.open(name), dtype=str, encoding="latin-1")
        d = d[d.LineCode.notna()].copy()
        d["st"] = d.GeoName.map(abbr)
        d = d[d.st.notna()]
        years = [c for c in d.columns if c.isdigit()]
        lines = BEA_LINES[cls]
        pick = {}
        for part, code in lines.items():
            sub = d[d.LineCode.str.strip() == code]
            assert len(sub) == 51 and sub.Description.str.strip().str.startswith(BEA_DESC[part]).all(), (table, part)
            pick[part] = sub.set_index("st")
        for part in ("manufacturing", "farm", "government"):
            for st in pick[part].index:
                for y in years:
                    num, nflag = val(pick[part].at[st, y])
                    den, dflag = val(pick["total"].at[st, y])
                    flag = "; ".join(x for x in [nflag, dflag] if x)
                    v = round(100 * num / den, 3) if num is not None and den else None
                    note = (f"computed here: {table} line {lines[part]} / line 10 x 100; num={'' if num is None else num}; "
                            f"den={'' if den is None else den}; classification={cls}; full- and part-time jobs, by place of work")
                    add(f"employment_share_{part}", cls, st, y, v, "percent of total employment", flag, note,
                        BEA_URL, f"{f.name}!{name}")


# ---------------------------------------------------------------- 6. unemployment rate (BLS LAUS annual averages)
BLS_URL = "https://www.bls.gov/lau/staadata.zip"


def build_unemployment():
    f = download(BLS_URL, SRC / "bls_staadata.zip")
    d = pd.read_excel(zipfile.ZipFile(f).open("staadata.xlsx"), header=None, dtype=str)
    assert str(d.iat[5, 9]).strip() == "Rate", d.iat[5, 9]
    foot = " ".join(str(x) for x in d[0] if str(x).startswith("("))
    for i in range(len(d)):
        st = abbr(d.iat[i, 1])
        y, mark = year_label(d.iat[i, 2])
        if not st or not y or not re.fullmatch(r"\d{2}", str(d.iat[i, 0]).strip()):
            continue
        v, flag = val(d.iat[i, 9])
        note = "annual average, not seasonally adjusted, model-based"
        if mark:
            flag = "; ".join(x for x in [flag, f"({mark})"] if x)
            note += "; fn " + mark + ": " + short(re.sub(r"^\(\d+\)\s*", "", foot), 200)
        add("unemployment_rate", "laus_annual_average", st, y, v, "percent", flag, note, BLS_URL, f"{f.name}!staadata.xlsx")


# ---------------------------------------------------------------- 7. party control of state government
KLARNER_DOI = "https://doi.org/10.7910/DVN/LZHMG3"
KLARNER_FILES = {2432030: "klarner_Partisan_Balance_For_Use2011_06_09b.xlsx",
                 2432028: "klarner_Partisan_Balance_For_Use2012_10_18_Codebook.docx",
                 2432029: "klarner_StatePartisanBalance1934to2011_SourceFiles_2011_05_24_Codebook.doc",
                 2432027: "klarner_StatePartisanBalance1934to2011_SourceFiles_2011_05_24.xlsx"}
BP_URL = "https://ballotpedia.org/Party_control_of_{}_state_government"
BP_METHOD = "https://ballotpedia.org/Ballotpedia:Who_Runs_the_States,_Partisanship_Results,_Methodology"
K_GOV = {1.0: "Democratic", 0.0: "Republican", 0.5: "Other"}
K_CH = {1.0: "Democratic", 0.0: "Republican", 0.5: "Split"}
B_GOV = {"D": "Democratic", "R": "Republican", "I": "Other"}
B_CH = {"D": "Democratic", "R": "Republican", "S": "Split", "-": "Nonpartisan"}
K_ASOF = ("year of the legislative session; a chamber that changed hands mid-session is given to the party in control "
          "when the state budget passed; the codebook gives no date for the governor")
B_ASOF = "party that held the office or the chamber majority for most of the calendar year"


def trifecta(g, s, h):
    if "Nonpartisan" in (s, h):
        return "Nonpartisan legislature"
    if not (g and s and h):
        return ""
    if g == s == h and g in ("Democratic", "Republican"):
        return g
    return "Divided"


def klarner():
    for fid, name in KLARNER_FILES.items():
        download(f"https://dataverse.harvard.edu/api/access/datafile/{fid}", SRC / name)
    d = pd.read_excel(SRC / KLARNER_FILES[2432030])
    d["st"] = d.state.map(abbr)
    assert d.st.notna().all() and d.st.nunique() == 50
    s = pd.read_excel(SRC / KLARNER_FILES[2432027])
    s.columns = [str(c).strip() for c in s.columns]
    s["st"] = s.state.map(abbr)
    nonpart = {(r.st, int(r.year), int(r.chamber)) for r in s.itertuples() if r.partisan_elections == 0}
    out = []
    for r in d[(d.year >= 1937) & (d.year <= 2011)].itertuples():
        y, flag = int(r.year), []
        raw = {"govparty_c": r.govparty_c, "sen_cont_alt": r.sen_cont_alt, "hs_cont_alt": r.hs_cont_alt}
        g = K_GOV.get(raw["govparty_c"], "")
        sen = K_CH.get(raw["sen_cont_alt"], "")
        hs = K_CH.get(raw["hs_cont_alt"], "")
        flag.append("klarner codes: " + ", ".join(f"{k}={'' if pd.isna(v) else v:g}" if not pd.isna(v) else f"{k}=missing" for k, v in raw.items()))
        np_s, np_h = (r.st, y, 8) in nonpart, (r.st, y, 9) in nonpart
        if np_s or np_h:
            if sen or hs:
                flag.append(f"legislators elected without party labels (klarner partisan_elections=0); klarner still codes "
                            f"caucus control senate={sen or 'missing'}, house={hs or 'missing'}")
            else:
                flag.append("legislators elected without party labels (klarner partisan_elections=0)")
            sen = "Nonpartisan" if np_s else sen
            hs = "Nonpartisan" if np_h else hs
            if r.st == "NE":
                hs = ""
                flag.append("one chamber only; it is reported under senate")
        if raw["govparty_c"] == 0.5:
            flag.append("governor not of a major party")
        for nm, v in (("senate", raw["sen_cont_alt"]), ("house", raw["hs_cont_alt"])):
            if v == 0.5:
                flag.append(f"{nm}: neither party held a majority of seats or control was shared (klarner 0.5)")
        if not g:
            flag.append("governor not coded by klarner")
        out.append(dict(state=r.st, year=y, governor=g, senate=sen, house=hs, trifecta=trifecta(g, sen, hs),
                        as_of=K_ASOF, flag="; ".join(flag), source="Klarner, State Partisan Balance Data, 1937-2011 (Harvard Dataverse)",
                        source_url=KLARNER_DOI))
    return pd.DataFrame(out)


def ballotpedia():
    download(BP_METHOD, SRC / "ballotpedia_who_runs_the_states_methodology.html")
    out = []
    for st, name in STATES.items():
        if st == "DC":
            continue
        url = BP_URL.format(name.replace(" ", "_"))
        f = download(url, SRC / f"ballotpedia_party_control_{st}.html", pause=4)
        soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="replace"), "lxml")
        tabs = [t for t in soup.find_all("table", class_="wikitable") if t.find("tr").get_text(" ", strip=True).startswith("Year")]
        assert len(tabs) == 1, (st, len(tabs))
        grid = {}
        for tr in tabs[0].find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            grid[cells[0]] = cells[1:]
        yrs = [(1900 if int(x) >= 92 else 2000) + int(x) for x in grid["Year"]]
        assert yrs[0] == 1992 and yrs == list(range(1992, yrs[-1] + 1)), (st, yrs[:3])
        lower = "House" if "House" in grid else "Assembly" if "Assembly" in grid else None
        assert (lower is None) == (st == "NE"), st
        refs = [li.get_text(" ", strip=True).lstrip("↑ ").strip() for li in soup.select("ol.references li")]
        for n, y in enumerate(yrs):
            flag, vals = [], {}
            for fld, row in (("governor", "Governor"), ("senate", "Senate"), ("house", lower)):
                cell = grid[row][n] if row else ""
                m = re.match(r"^([A-Z-])(?:\s*\[(\d+)\])?$", cell) if cell else None
                assert m or not row, (st, y, row, cell)
                code = m.group(1) if m else ""
                vals[fld] = (B_GOV if fld == "governor" else B_CH).get(code, "")
                assert vals[fld] or not row, (st, y, row, cell)
                if m and m.group(2):
                    flag.append(f"{fld} footnote [{m.group(2)}]: {refs[int(m.group(2)) - 1]}")
                if code == "S":
                    flag.append(f"{fld}: tied, power-sharing agreement or bipartisan coalition (ballotpedia S)")
                if code == "I":
                    flag.append("governor not of a major party (ballotpedia I)")
            if st == "NE":
                flag.append("one chamber only, elected without party labels; it is reported under senate")
            flag.insert(0, "ballotpedia codes: " + ", ".join(f"{k}={grid[r][n] if r else 'none'}" for k, r in
                                                              (("governor", "Governor"), ("senate", "Senate"), ("house", lower))))
            out.append(dict(state=st, year=y, governor=vals["governor"], senate=vals["senate"], house=vals["house"],
                            trifecta=trifecta(vals["governor"], vals["senate"], vals["house"] if st != "NE" else "Nonpartisan"),
                            as_of=B_ASOF, flag="; ".join(flag), source="Ballotpedia, Party control of state government pages",
                            source_url=url))
    return pd.DataFrame(out)


NCSL_BASE = "https://documents.ncsl.org/wwwncsl/Elections/"
NCSL_FILES = {2015: "Legis_Control_2015.pdf", 2016: "Legis_Control_2016.pdf", 2017: "Legis_Control_2017_March_1_9%20am.pdf",
              2018: "Legis_Control_011018_26973.pdf", 2019: "Legis_Control_2019_February%201st.pdf",
              2020: "Legis_Control_2020_April%201.pdf", 2021: "Legis_Control_2-2021.pdf", 2025: "Legis_Control_2025_8.29.25.pdf"}
NCSL_WORD = {"Dem": "Democratic", "Rep": "Republican", "Ind": "Other", "Split": "Split", "Divided": "Divided", "N/A": "N/A"}


def ncsl():
    """NCSL's dated yearly tables, for the years whose PDF is still on its server. Used only as a check."""
    import fitz  # PyMuPDF

    def page_lines(pg):
        """Words on the same baseline, left to right, joined into one printed line."""
        rows = []   # [baseline y, [(x, word), ...]]; a word joins the current line if it sits within 3 points of it
        for x0, y0, x1, y1, word, *_ in sorted(pg.get_text("words"), key=lambda w: ((w[1] + w[3]) / 2, w[0])):
            y = (y0 + y1) / 2
            if rows and abs(y - rows[-1][0]) <= 3:
                rows[-1][1].append((x0, word))
            else:
                rows.append([y, [(x0, word)]])
        return [" ".join(w for _, w in sorted(ws)) for _, ws in rows]

    names = sorted((n for a, n in STATES.items() if a != "DC"), key=len, reverse=True)
    out = []
    for y, fn in NCSL_FILES.items():
        f = download(NCSL_BASE + fn, SRC / f"ncsl_Legis_Control_{y}.pdf")
        lines = [l for pg in fitz.open(f) for l in page_lines(pg)]
        asof = " ".join(lines[:2]) if "Total Total" not in lines[1] else lines[0]
        notes = " ".join(l for n, l in enumerate(lines) if l.startswith("*Notes") or (n and lines[n - 1].startswith("*Notes")))
        got = {}
        for l in lines:
            for n in names:
                if re.match(rf"^{n}\*?\s", l) and n not in got:
                    # the last three control codes on the row; stray footnote letters between them are skipped
                    leg, gov, ctl = [t for t in l.split() if t.rstrip("*") in NCSL_WORD][-3:]
                    got[n] = dict(state=NAME_TO_ABBR[n.upper()], year=y, ncsl_as_of=short(asof, 90),
                                  ncsl_legislature=NCSL_WORD[leg.rstrip("*")], ncsl_governor=NCSL_WORD[gov.rstrip("*")],
                                  ncsl_state_control=NCSL_WORD[ctl.rstrip("*")],
                                  ncsl_note=short(notes, 300) if "*" in l else "",
                                  ncsl_url=NCSL_BASE + fn)
                    break
        assert len(got) == 50, (y, len(got))
        out += got.values()
    return pd.DataFrame(out)


def ncsl_check(main):
    n = ncsl()
    m = main[main.state != "DC"].copy()
    m["legislature"] = [s if s == h and s in ("Democratic", "Republican") else "Nonpartisan" if "Nonpartisan" in (s, h) else "Split"
                        for s, h in zip(m.senate, m.house)]
    c = n.merge(m[["state", "year", "governor", "legislature", "trifecta"]], on=["state", "year"], how="left")
    c["ncsl_legislature"] = c.ncsl_legislature.replace({"Divided": "Split", "N/A": "Nonpartisan"})
    c["ncsl_state_control"] = c.ncsl_state_control.replace({"N/A": "Nonpartisan legislature"})
    c["governor_agree"] = c.ncsl_governor == c.governor
    c["legislature_agree"] = c.ncsl_legislature == c.legislature
    c["trifecta_agree"] = c.ncsl_state_control == c.trifecta
    c = c[["state", "year", "governor", "ncsl_governor", "governor_agree", "legislature", "ncsl_legislature", "legislature_agree",
           "trifecta", "ncsl_state_control", "trifecta_agree", "ncsl_as_of", "ncsl_note", "ncsl_url"]].sort_values(["state", "year"])
    c.to_csv(KPI / "party_control_ncsl_check.csv", index=False)
    print(f"NCSL check, years {sorted(set(c.year))}: {len(c)} state-years; disagreements " +
          ", ".join(f"{k}={int((~c[k + '_agree']).sum())}" for k in ("governor", "legislature", "trifecta")))
    return c


def build_party():
    k, b = klarner(), ballotpedia()
    this_year = pd.Timestamp.today().year
    b.loc[b.year >= this_year, "flag"] += "; year in progress when downloaded"
    main = pd.concat([k, b[b.year >= 2012]], ignore_index=True)
    cols = ["state", "year", "governor", "senate", "house", "trifecta", "as_of", "flag", "source", "source_url"]
    dc = pd.DataFrame([dict(state="DC", year=y, governor="", senate="", house="", trifecta="", as_of="",
                            flag="not a state: no state government", source="", source_url="")
                       for y in range(int(main.year.min()), int(main.year.max()) + 1)])
    main = pd.concat([main, dc], ignore_index=True).sort_values(["state", "year"])[cols]
    assert not main.duplicated(["state", "year"]).any()
    assert set(main.trifecta) <= {"Democratic", "Republican", "Divided", "Nonpartisan legislature", ""}
    main.to_csv(KPI / "party_control.csv", index=False)

    o = k.merge(b, on=["state", "year"], suffixes=("_klarner", "_ballotpedia"))
    for c in ("governor", "senate", "house", "trifecta"):
        o[f"{c}_agree"] = o[f"{c}_klarner"] == o[f"{c}_ballotpedia"]
    keep = ["state", "year"] + [f"{c}_{s}" for c in ("governor", "senate", "house", "trifecta") for s in ("klarner", "ballotpedia", "agree")]
    o = o[keep + ["flag_klarner", "flag_ballotpedia"]].sort_values(["state", "year"])
    o.to_csv(KPI / "party_control_overlap.csv", index=False)
    print(f"party_control.csv: {len(main)} rows, {main.year.min()}-{main.year.max()}")
    print(main.groupby("source").year.agg(["min", "max", "count"]).to_string())
    print(main.trifecta.replace("", "(empty)").value_counts().to_string())
    print(f"overlap {o.year.min()}-{o.year.max()}: {len(o)} state-years; disagreements " +
          ", ".join(f"{c}={int((~o[c + '_agree']).sum())}" for c in ("governor", "senate", "house", "trifecta")))
    ncsl_check(main)
    return main, o


# ---------------------------------------------------------------- run
if __name__ == "__main__":
    for fn in (build_income, build_poverty, build_education, build_uninsured, build_employment, build_unemployment):
        n = len(rows)
        fn()
        print(f"{fn.__name__}: {len(rows) - n} rows")
    kpi = pd.DataFrame(rows)
    assert set(kpi.state) <= set(STATES), set(kpi.state) - set(STATES)
    dup = kpi[kpi.duplicated(["series", "state", "year", "variant"], keep=False)]
    assert dup.empty, dup.head(20)
    marked = kpi[kpi.value.isna()]
    assert (marked.flag != "").all(), "an empty value with no publisher mark"
    kpi = kpi.sort_values(["series", "variant", "state", "year"])
    kpi["value"] = kpi.value.map(lambda v: "" if pd.isna(v) else str(int(v)) if float(v).is_integer() else repr(float(v)))
    kpi.to_csv(KPI / "kpi_state_year.csv", index=False)
    summ = kpi.groupby(["series", "variant"]).agg(first=("year", "min"), last=("year", "max"), rows=("year", "size"),
                                                  states=("state", "nunique"), empty=("value", lambda s: int((s == "").sum())))
    print(summ.to_string())
    build_party()
