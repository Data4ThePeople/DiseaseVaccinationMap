"""Vaccination coverage before the ChildVaxView birth-year series, plus licensure years.

Downloads every source into data/raw/vax_history/src/ and builds

  data/raw/vax_history/nis_state_survey_year.csv   NIS, children 19-35 months, 1995-2017
  data/raw/vax_history/national_pre1995.csv        USIS 1959-1985, NHIS 1991-1994
  data/raw/vax_history/licensure.csv               year each vaccine was first licensed

Re-runnable: a file that is already in src/ is not fetched again.
No number in the outputs is typed in by hand. Every row is parsed out of a
downloaded file and carries that file's name and URL.

Run:  .venv/bin/python scripts/04b_fetch_vax_history.py
"""
from __future__ import annotations

import csv
import re
import sys
import warnings
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RAW, STATES, download  # noqa: E402

warnings.filterwarnings("ignore")

OUT = RAW / "vax_history"
SRC = OUT / "src"

WB = "https://web.archive.org/web/{ts}id_/{url}"
CDC_TABLES = "http://www.cdc.gov/vaccines/imz-managers/coverage/nis/child/tables/"

# --------------------------------------------------------------------------
# A. NIS table sets, one per survey year. CDC took these files off cdc.gov;
#    the copies are the Internet Archive captures of the same cdc.gov URLs.
#    (wayback timestamp, path under CDC_TABLES). "state" = table by state,
#    "iap" = table by state and Immunization Action Plan (urban) area.
# --------------------------------------------------------------------------
NIS_TABLES = {
    1995: {"state": ("20150910092549", "95/TAB3-antigen_state.xls"),
           "iap": ("20150910080510", "95/TAB2-antigen_iap.xls")},
    1996: {"state": ("20150908093112", "96/TAB3-antigen_state.xls"),
           "iap": ("20150908085830", "96/TAB2-antigen_iap.xls")},
    1997: {"state": ("20150907225205", "97/TAB3-antigen_state.xls"),
           "iap": ("20150908061319", "97/TAB2-antigen_iap.xls")},
    1998: {"state": ("20150910075650", "98/TAB3-antigen_state.xls"),
           "iap": ("20150910015652", "98/TAB2-antigen_iap.xls")},
    1999: {"state": ("20150908112827", "99/antigen_state.xls"),
           "iap": ("20150908120856", "99/antigen_iap.xls")},
    # 2000 was only ever hosted on ftp.cdc.gov, which still serves it.
    2000: {"state": (None, "https://ftp.cdc.gov/pub/vaccines_nis/00/antigen_state.xls"),
           "iap": (None, "https://ftp.cdc.gov/pub/vaccines_nis/00/antigen_iap.xls")},
    2001: {"state": ("20150908092647", "01/TAB3-antigen_state.xls"),
           "iap": ("20150908093306", "01/TAB2-antigen_iap.xls")},
    2002: {"state": ("20150908050412", "02/tab3_antigen_state.xls"),
           "iap": ("20150908075115", "02/tab2_antigen_iap.xls")},
    2003: {"state": ("20150908143651", "03/tab03_antigen_state.xls"),
           "iap": ("20150908135721", "03/tab02_antigen_iap.xls")},
    2004: {"state": ("20150908090326", "04/tab03_antigen_state.xls"),
           "iap": ("20150908073346", "04/tab02_antigen_iap.xls")},
    2005: {"state": ("20150908182205", "05/tab03_antigen_state.xls"),
           "iap": ("20150908140233", "05/tab02_antigen_iap.xls")},
    2006: {"state": ("20150908151918", "06/tab03_antigen_state.xls"),
           "iap": ("20150908151345", "06/tab02_antigen_iap.xls")},
    2007: {"state": ("20150908072351", "07/tab03_antigen_state.xls"),
           "iap": ("20150908040350", "07/tab02_antigen_iap.xls")},
    2008: {"state": ("20150908064131", "08/tab03_antigen_state.xls"),
           "iap": ("20150908063827", "08/tab02_antigen_iap.xls")},
    2009: {"state": ("20150908181752", "09/tab03_antigen_state.xls"),
           "iap": ("20150908143133", "09/tab02_antigen_iap.xls")},
    2010: {"state": ("20150909170915", "10/tab03_antigen_state.xlsx"),
           "iap": ("20150909171948", "10/tab02_antigen_iap.xlsx")},
    2011: {"state": ("20150223072556", "11/tab03_antigen_state_2011.xlsx"),
           "iap": ("20150910083324", "11/tab02_antigen_iap_2011.xlsx")},
    2012: {"state": ("20150222125502", "12/tab03_antigen_state_2012.xlsx"),
           "iap": ("20150910120940", "12/tab02_antigen_iap_2012.xlsx")},
    2013: {"state": ("20141011055459", "13/tab03_antigen_state_2013.xlsx"),
           "iap": ("20141010073931", "13/tab02_antigen_iap_2013.xlsx")},
    2014: {"state": ("20150831051438", "14/tab03_antigen_state_2014.xlsx"),
           "iap": ("20150831051433", "14/tab02_antigen_iap_2014.xlsx")},
}


def nis_table_sources():
    """Yield (year, kind, url, local path) for every NIS table file."""
    for year, kinds in NIS_TABLES.items():
        for kind, (ts, path) in kinds.items():
            if ts is None:
                url = path
            else:
                url = WB.format(ts=ts, url=CDC_TABLES + path)
            ext = path.rsplit(".", 1)[1]
            yield year, kind, url, SRC / f"nis{year}_antigen_{kind}.{ext}"


def fetch_all():
    SRC.mkdir(parents=True, exist_ok=True)
    for _year, _kind, url, dest in nis_table_sources():
        download(url, dest, pause=1.5)
    for url, name in OTHER_SOURCES:
        download(url, SRC / name, pause=1.5)
    for url, page_no, name in BIG_PDF_PAGES:
        fetch_pdf_page(url, page_no, SRC / name)


def fetch_pdf_page(url, page_no, dest):
    """Keep one page of a very large scanned PDF (the Health, United States volumes
    are 36 MB and 98 MB). The whole file is downloaded, the page is cut out, the
    rest is deleted. page_no is the PDF page number, starting at 1."""
    if dest.exists() and dest.stat().st_size > 0:
        return
    tmp = SRC / "_big_download.pdf"
    tmp.unlink(missing_ok=True)
    download(url, tmp, pause=1.5)
    big, one = fitz.open(tmp), fitz.open()
    one.insert_pdf(big, from_page=page_no - 1, to_page=page_no - 1)
    one.save(dest)
    big.close()
    tmp.unlink()


MMWR_OLD = "https://www.cdc.gov/mmwr/preview/mmwrhtml/{}.htm"
MMWR_NEW = "https://www.cdc.gov/mmwr/volumes/{}/wr/{}.htm"

# The MMWR report on each NIS survey year (list taken from the archived CDC
# page .../coverage/nis/child/articles.html plus the ChildVaxView report pages).
MMWR_NIS = {
    1995: MMWR_OLD.format("00046725"),
    1996: MMWR_OLD.format("00048503"),
    1997: MMWR_OLD.format("00053832"),
    1998: MMWR_OLD.format("mm4837a2"),
    1999: MMWR_OLD.format("mm4926a1"),
    2000: MMWR_OLD.format("mm5030a1"),
    2001: MMWR_OLD.format("mm5130a2"),
    2002: MMWR_OLD.format("mm5231a2"),
    2003: MMWR_OLD.format("mm5329a3"),
    2004: MMWR_OLD.format("mm5429a1"),
    2005: MMWR_OLD.format("mm5536a2"),
    2006: MMWR_OLD.format("mm5634a2"),
    2007: MMWR_OLD.format("mm5735a1"),
    2008: MMWR_OLD.format("mm5833a3"),
    2009: MMWR_OLD.format("mm5936a2"),
    2010: MMWR_OLD.format("mm6034a2"),
    2011: MMWR_OLD.format("mm6135a1"),
    2012: MMWR_OLD.format("mm6236a1"),
    2013: MMWR_OLD.format("mm6334a1"),
    2014: MMWR_OLD.format("mm6433a1"),
    2015: MMWR_NEW.format(65, "mm6539a4"),
    2016: MMWR_NEW.format(66, "mm6643a3"),
    2017: MMWR_NEW.format(67, "mm6740a4"),
}

# NIS-Child public-use-file user's guides. Appendix Table F.7 is the state
# table for that survey year; Table G.4 (2017 guide) is the national series.
DUG = {
    2015: WB.format(ts="20190620155440",
                    url="https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF15-DUG.pdf"),
    2016: "https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF16-DUG.pdf",
    2017: "https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF17-DUG.pdf",
}

# Supplementary Table 2 of the MMWR report on the 2017 survey (state table).
STACKS_2017_T2 = "https://stacks.cdc.gov/view/cdc/59415/cdc_59415_DS1.pdf"

MMWR_GIF = "https://www.cdc.gov/mmwr/preview/mmwrhtml/figures/{}.gif"

# B. coverage before 1995
SIMPSON = "http://www.jonathans-stories.com/non-fiction/Simpson4SurveysAJPM2001.pdf"
HUS95 = "https://www.cdc.gov/nchs/data/hus/hus95.pdf"
HUS78 = "https://www.cdc.gov/nchs/data/hus/hus78.pdf"       # Table 36 is PDF page 214
HUS86 = "https://www.cdc.gov/nchs/data/hus/hus86acc.pdf"    # Table 34 is PDF page 124
BIG_PDF_PAGES = [
    (HUS78, 214, "hus78_table36_pdfpage214.pdf"),
    (HUS86, 124, "hus86_table34_pdfpage124.pdf"),
]

# C. licensure
PINK = "https://www.cdc.gov/pinkbook/hcp/table-of-contents/{}.html"
LICENSURE_SOURCES = {
    "lic_mmwr_achievements_1999.htm": MMWR_OLD.format("00056803"),
    "lic_pinkbook_polio.html": PINK.format("chapter-18-poliomyelitis"),
    "lic_pinkbook_measles.html": PINK.format("chapter-13-measles"),
    "lic_pinkbook_mumps.html": PINK.format("chapter-15-mumps"),
    "lic_pinkbook_rubella.html": PINK.format("chapter-20-rubella"),
    "lic_pinkbook_pertussis.html": PINK.format("chapter-16-pertussis"),
    "lic_pinkbook_diphtheria.html": PINK.format("chapter-7-diphtheria"),
    "lic_pinkbook_hepatitis_a.html": PINK.format("chapter-9-hepatitis-a"),
    "lic_mmwr_dtap_1992.htm": MMWR_OLD.format("00041801"),
    "lic_mmwr_dtap_infants_1996.htm": MMWR_OLD.format("00043252"),
    "lic_mmwr_hepa_1995.htm": MMWR_OLD.format("00038243"),
}

# method documents quoted in NOTES.md
METHOD_SOURCES = {
    "method_mmwr_birth_year_2019.htm": MMWR_NEW.format(68, "mm6841e2"),
    "method_nis_tech_notes.html":
        "https://archive.cdc.gov/www_cdc_gov/vaccines/imz-managers/coverage/nis/child/tech-notes.html",
    # CDC's own list of NIS articles, the source of the MMWR_NIS list above
    "method_nis_articles_list.html": WB.format(
        ts="20140330230101", url="http://www.cdc.gov/vaccines/imz-managers/coverage/nis/child/articles.html"),
}

SOURCE_URL: dict[str, str] = {}
SOURCE_URL.update({f"mmwr_nis{y}.htm": u for y, u in MMWR_NIS.items()})
SOURCE_URL.update({f"NIS-PUF{str(y)[2:]}-DUG.pdf": u for y, u in DUG.items()})
SOURCE_URL["mmwr_nis2017_supp_table2.pdf"] = STACKS_2017_T2
# Table 1 images of two MMWR reports, read by eye for the 1997-2003 national check
SOURCE_URL["mmwr_nis2003_table1.gif"] = MMWR_GIF.format("m329a3t1")
SOURCE_URL["mmwr_nis2001_table1.gif"] = MMWR_GIF.format("m130a2t1")
SOURCE_URL["simpson2001_ajpm.pdf"] = SIMPSON
SOURCE_URL["hus95.pdf"] = HUS95
SOURCE_URL.update(LICENSURE_SOURCES)
SOURCE_URL.update(METHOD_SOURCES)
OTHER_SOURCES = [(u, n) for n, u in SOURCE_URL.items()]
SOURCE_URL.update({n: u for u, _p, n in BIG_PDF_PAGES})
SOURCE_URL.update({d.name: u for _y, _k, u, d in nis_table_sources()})



# ==========================================================================
# A. BUILD: NIS state table, survey years 1995-2017
# ==========================================================================
STATE_NAMES = set(STATES.values())
AREA_ALIASES = {
    "US NATIONAL": "United States", "U.S. NATIONAL": "United States",
    "UNITED STATES": "United States", "U.S. OVERALL": "United States",
    "DIST. OF COLUMBIA": "District of Columbia",
}
MARKS = "*†‡§¶¥€ς#^|"           # footnote symbols CDC puts after an area name
NIS_FIELDS = ["year", "state", "vaccine", "estimate", "ci_half_width", "ci_low", "ci_high",
              "flag", "source_url", "source_file", "source_table"]


def squash(text) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def area_name(label: str):
    """Return the standard state name, 'United States', or None for any other area."""
    raw = squash(label)
    name = raw.rstrip(MARKS + " ").strip()
    name = AREA_ALIASES.get(name.upper(), name)
    if name == "United States" or name in STATE_NAMES:
        return name, raw[len(raw.rstrip(MARKS + " ")):].strip()
    return None, ""


def header_vaccine(cell: str):
    h = squash(cell).replace(" ", "").replace("≥", "")
    if re.match(r"^3\+?DT", h):
        return "dtp_3"
    if re.match(r"^4\+?DT", h):
        return "dtp_4"
    if re.match(r"^3\+?Polio", h):
        return "polio_3"
    if re.match(r"^1\+?MMR", h):
        return "mmr_1"
    if re.match(r"^2\+?HepA", h):
        return "hepa_2"
    return None


def parse_pm_cell(cell):
    """'85.7±0.9' -> (85.7, 0.9, flag). 'NA' -> (None, None, 'NA ...'). Never invents a number."""
    raw = squash(cell)
    tight = raw.replace(" ", "")
    if tight.upper().startswith("NA") or tight in {"", "-", "--", "—"}:
        return None, None, f"not available in source (cell reads '{raw}')"
    m = re.match(r"^(\d+(?:\.\d+)?)(±|\+)(\d+(?:\.\d+)?)(.*)$", tight)
    if not m:
        raise ValueError(f"unreadable cell {raw!r}")
    flags = []
    if m.group(4):
        flags.append(f"mark {m.group(4)}")
    if m.group(2) == "+" or " " in raw.replace(" ±", "±").replace("± ", "±"):
        flags.append(f"typo in source cell, reads '{raw}'")
    return float(m.group(1)), float(m.group(3)), "; ".join(flags)


def read_nis_xls(path: Path, year: int):
    """Parse one CDC 'antigen by state' workbook. Returns (rows, title)."""
    book = pd.read_excel(path, sheet_name=None, header=None, dtype=str)
    for sheet, df in book.items():
        hdr = None
        for i, row in df.iterrows():
            vacs = [header_vaccine(c) for c in row if isinstance(c, str)]
            if "polio_3" in vacs and "mmr_1" in vacs:
                hdr = i
                break
        if hdr is None:
            continue
        alltext = [squash(c) for c in df.values.ravel() if isinstance(c, str)]
        title = " ".join(t for t in alltext[:8] if re.search(r"Estimated|Among|National Immunization", t)
                         and "±" not in t)
        title = squash(title)
        # the workbook must say which survey year it is
        if not re.search(rf"(Q1/{year}-Q4/{year}|[ ,]{year}\b)", title):
            raise ValueError(f"{path.name}: year {year} not found in title: {title}")
        cols = {j: header_vaccine(c) for j, c in enumerate(df.iloc[hdr]) if isinstance(c, str)
                and header_vaccine(c)}
        out = []
        for i in range(hdr + 1, len(df)):
            cells = df.iloc[i]
            label = next((c for c in cells if isinstance(c, str) and c.strip()), None)
            if label is None:
                continue
            name, mark = area_name(label)
            if name is None:
                continue
            for j, vac in cols.items():
                if not isinstance(cells[j], str):
                    # an empty cell stays empty; it is recorded so the gap is visible
                    est, hw, flag = None, None, "cell is empty in the source table"
                else:
                    est, hw, flag = parse_pm_cell(cells[j])
                if mark:
                    flag = "; ".join(x for x in [f"row mark {mark}", flag] if x)
                out.append({"year": year, "state": name, "vaccine": vac, "estimate": est,
                            "ci_half_width": hw, "ci_low": None, "ci_high": None, "flag": flag,
                            "source_table": f"{title} [sheet {sheet}]"})
        return out, title
    raise ValueError(f"no table found in {path.name}")


def read_dug_f7(path: Path, year: int):
    """Appendix Table F.7 of a NIS-Child public-use-file user's guide (PDF)."""
    doc = fitz.open(path)
    lines, title = [], None
    for page in doc:
        text = page.get_text()
        if title is None and "Table F.7:" in text and text.count("±") > 50:
            m = re.search(r"Table F\.7:.*?Q1/\d{4}-Q4/\d{4}", text, re.S)
            title = squash(m.group(0))
        if title is not None:
            # the table runs over several pages; it ends where the ± cells stop
            if text.count("±") < 50:
                break
            lines += [squash(x) for x in text.split("\n")]
    if title is None or f"Q1/{year}-Q4/{year}" not in title:
        raise ValueError(f"{path.name}: Table F.7 for {year} not found")
    # column order is printed once per page, read it from the first header block
    start = lines.index(next(x for x in lines if x.startswith("≥4 DTaP")))
    header = []
    for x in lines[start:]:
        if re.match(r"^U\.S\. National", x):
            break
        header.append(x)
    header = squash(" ".join(header))
    names = re.findall(r"≥\d [A-Za-z]+|Hib-FS|HepB Birth Dose|Rotavirus|4:3:1:3\*:3:1:4", header)
    if len(names) != 11:
        raise ValueError(f"{path.name}: expected 11 columns in Table F.7, got {names}")
    want = {i: header_vaccine(n.replace(" ", "")) for i, n in enumerate(names)}
    val = re.compile(r"^(\d+\.\d) ± (\d+\.\d)$|^NA$")
    out, i = [], 0
    while i < len(lines):
        name, mark = area_name(re.sub(r"^U\.S\. National.*", "US National", lines[i]))
        if name is None:
            i += 1
            continue
        vals, j = [], i + 1
        while j < len(lines) and len(vals) < 11:
            if val.match(lines[j]):
                vals.append(lines[j])
            elif lines[j]:
                break
            j += 1
        if len(vals) != 11:
            raise ValueError(f"{path.name}: {name} has {len(vals)} values, expected 11")
        for k, vac in want.items():
            if vac is None:
                continue
            est, hw, flag = parse_pm_cell(vals[k])
            out.append({"year": year, "state": name, "vaccine": vac, "estimate": est,
                        "ci_half_width": hw, "ci_low": None, "ci_high": None, "flag": flag,
                        "source_table": title})
        i = j
    return out


def mmwr_tables(path: Path):
    soup = BeautifulSoup(path.read_text(errors="replace"), "lxml")
    for t in soup.find_all("table"):
        rows = [[squash(c.get_text(" ")) for c in r.find_all(["td", "th"])] for r in t.find_all("tr")]
        cap = t.find("caption")
        yield (squash(cap.get_text(" ")) if cap else ""), [r for r in rows if r]


def read_mmwr2015_state(path: Path):
    """MMWR 65(39) Table 3: state table with HepA >=2 doses, '59.6 (±1.5)' cells."""
    soup = BeautifulSoup(path.read_text(errors="replace"), "lxml")
    out = []
    for _cap, rows in mmwr_tables(path):
        hdr = next((r for r in rows if any("HepA (≥2 doses)" in c for c in r)), None)
        if hdr is None or not any(r[0].startswith("Alabama") for r in rows):
            continue
        cols = {j + 1: v for j, v in enumerate(
            {"MMR (≥1 dose)": "mmr_1", "DTaP (≥4 doses)": "dtp_4", "HepA (≥2 doses)": "hepa_2"}.get(
                re.sub(r"\s*[§¶*†]+$", "", c).strip()) for c in hdr) if v}
        title = next(squash(x.get_text(" ")) for x in soup.find_all(["h5", "h4", "p", "div", "strong"])
                     if squash(x.get_text(" ")).startswith("TABLE 3") and len(squash(x.get_text(" "))) < 600)
        for r in rows:
            name, mark = area_name(r[0])
            if name is None or len(r) < 7:
                continue
            for j, vac in cols.items():
                m = re.match(r"^(\d+\.\d) \(±(\d+\.\d)\)\s*(.*)$", r[j])
                if not m:
                    raise ValueError(f"MMWR 2015 cell {r[j]!r}")
                out.append({"year": 2015, "state": name, "vaccine": vac, "estimate": float(m.group(1)),
                            "ci_half_width": float(m.group(2)), "ci_low": None, "ci_high": None,
                            "flag": f"mark {m.group(3)}" if m.group(3) else "", "source_table": title})
    return out


def read_stacks2017(path: Path):
    """MMWR 67(40) Supplementary Table 2 (PDF): '91.5' then '(90.6–92.3)' on the next line."""
    doc = fitz.open(path)
    lines = []
    for page in doc:
        lines += [squash(x) for x in page.get_text().split("\n")]
    title = squash(" ".join(lines[:3]))
    title = title[:title.index("2017") + 4]
    hdr = squash(" ".join(lines[:40]))
    order = re.findall(r"MMR \(≥1 dose\)|DTaP \(≥4 doses\)|Hep B \(birth dose\)|HepA \(≥2 doses\)|"
                       r"Rotavirus|Combined 7-vaccine", hdr)
    if order[:6] != ["MMR (≥1 dose)", "DTaP (≥4 doses)", "Hep B (birth dose)", "HepA (≥2 doses)",
                     "Rotavirus", "Combined 7-vaccine"]:
        raise ValueError(f"unexpected column order in 2017 supplementary table: {order}")
    want = {0: "mmr_1", 1: "dtp_4", 3: "hepa_2"}
    est_re = re.compile(r"^(\d+\.\d)$")
    ci_re = re.compile(r"^\((\d+\.\d)\s*[–-]\s*(\d+\.\d)\)\s*(.*)$")
    out, i = [], 0
    while i < len(lines):
        name, mark = area_name(lines[i])
        if name is None:
            i += 1
            continue
        pairs, j = [], i + 1
        while j + 1 < len(lines) and len(pairs) < 6:
            e, c = est_re.match(lines[j]), ci_re.match(lines[j + 1])
            if not (e and c):
                break
            pairs.append((float(e.group(1)), float(c.group(1)), float(c.group(2)), c.group(3)))
            j += 2
        if len(pairs) != 6:
            raise ValueError(f"2017 supplementary table: {name} has {len(pairs)} value pairs")
        for k, vac in want.items():
            est, lo, hi, mk = pairs[k]
            out.append({"year": 2017, "state": name, "vaccine": vac, "estimate": est,
                        "ci_half_width": None, "ci_low": lo, "ci_high": hi,
                        "flag": f"mark {mk}" if mk else "", "source_table": title})
        i = j
    return out


def mmwr_national_table(path: Path):
    """Table 1 of an MMWR NIS report: national coverage by vaccine for five survey years.
    Returns {(year, vaccine): (estimate, half_width, ci_low, ci_high, mark)} and the caption."""
    cell = re.compile(r"(\d+\.\d)\s*\(\s*(?:±\s*(\d+\.\d)|(\d+\.\d)\s*[–-]\s*(\d+\.\d))\s*\)\s*([^\d(]*)")
    for cap, rows in mmwr_tables(path):
        years = None
        for r in rows[:4]:
            ys = [int(m) for c in r for m in re.findall(r"\b((?:19|20)\d\d)\b", c)]
            if len(ys) == 5 and len(" ".join(r)) < 120:
                years = ys
        if years is None:
            continue
        if not cap:
            cap = next((" ".join(r) for r in rows[:2] if "TABLE 1" in " ".join(r)), "TABLE 1")
        out, section = {}, ""
        for r in rows:
            label = r[0]
            vals = cell.findall(" ".join(r[1:]))
            if not vals:
                if not re.match(r"^[\d%(]", label):
                    section = label
                continue
            if len(vals) != 5:
                continue
            text = f"{section} {label}" if label.startswith("≥") else label
            text = text.replace(" ", "")
            if re.match(r"^DT.*≥3doses", text):
                vac = "dtp_3"
            elif re.match(r"^DT.*≥4doses", text):
                vac = "dtp_4"
            elif text.startswith("Polio"):
                vac = "polio_3"
            elif text.startswith("MMR"):
                vac = "mmr_1"
            elif re.match(r"^HepA.*≥2doses", text):
                vac = "hepa_2"
            else:
                continue
            for y, v in zip(years, vals):
                out[(y, vac)] = (float(v[0]), float(v[1]) if v[1] else None,
                                 float(v[2]) if v[2] else None, float(v[3]) if v[3] else None,
                                 v[4].strip())
            if not label.startswith("≥"):
                section = ""
        return out, squash(cap)
    raise ValueError(f"no national table in {path.name}")


def mmwr1998_text_table(path: Path):
    """The 1998 MMWR notice prints its Table 1 (1995-1998) as plain text."""
    text = squash(BeautifulSoup(path.read_text(errors="replace"), "lxml").get_text(" "))
    text = text[text.index("TABLE 1. Vaccination coverage levels"):]
    four = r"((?:\s*\d+\.\d \(.\d\.\d\)){4})"
    pats = {"dtp_3": r"DTP/DT . >=3 Doses" + four,
            "dtp_4": r">=4 Doses" + four,
            "polio_3": r"Poliovirus >=3 Doses" + four,
            "mcv_1": r"Measles-containing vaccine \(MCV\) >=1 Doses" + four}
    out = {}
    for vac, pat in pats.items():
        m = re.search(pat, text)
        for y, v in zip(range(1995, 1999), re.findall(r"(\d+\.\d) \(", m.group(1))):
            out[(y, vac)] = float(v)
    return out


def dug_g4(path: Path):
    """Table G.4 of the 2017 user's guide: national series 1995-2017 (4+ DTaP, 3+ polio, 1+ MMR)."""
    doc = fitz.open(path)
    text = next(p.get_text() for p in doc if "Table G.4:" in p.get_text() and "1995" in p.get_text()
                and "N.A." in p.get_text())
    lines = [squash(x) for x in text.split("\n") if squash(x)]
    out = {}
    for i, x in enumerate(lines):
        m = re.match(r"^((?:19|20)\d\d)(§§)?$", x)
        if m and re.match(r"^\d\d\.\d$", lines[i + 1]):
            y = int(m.group(1))
            out[(y, "dtp_4")], out[(y, "polio_3")], out[(y, "mmr_1")] = (float(v) for v in lines[i + 1:i + 4])
    if sorted({y for y, _ in out}) != list(range(1995, 2018)):
        raise ValueError("Table G.4 years incomplete")
    return out


def build_nis(qa: list[str]):
    rows = []

    def add(parsed, fname):
        for r in parsed:
            r["source_file"], r["source_url"] = fname, SOURCE_URL[fname]
            rows.append(r)

    # 1995-2014: CDC table "by state"; the "by state and IAP area" table must agree
    qa.append("== 1. CDC table by state against CDC table by state and urban area (same survey year)")
    for year, kinds in NIS_TABLES.items():
        files = {k: next(d for y, kk, _u, d in nis_table_sources() if y == year and kk == k) for k in kinds}
        st, _ = read_nis_xls(files["state"], year)
        iap, _ = read_nis_xls(files["iap"], year)
        key = lambda r: (r["state"], r["vaccine"])  # noqa: E731
        a = {key(r): (r["estimate"], r["ci_half_width"]) for r in st}
        b = {key(r): (r["estimate"], r["ci_half_width"]) for r in iap}
        diff = [(k, a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        qa.append(f"{year}: {len(a)} cells, {len(diff)} differ" + ("".join(f"\n      {d}" for d in diff)))
        add(st, files["state"].name)

    # 2015-2017: Table F.7 of the public-use-file user's guide (PDF)
    f7 = {}
    for year in (2015, 2016, 2017):
        fname = f"NIS-PUF{str(year)[2:]}-DUG.pdf"
        parsed = read_dug_f7(SRC / fname, year)
        f7.update({(year, r["state"], r["vaccine"]): r["estimate"] for r in parsed})
        add(parsed, fname)

    # hepatitis A, 2+ doses, by state: MMWR Table 3 (2015) and MMWR supplementary table 2 (2017)
    m15 = read_mmwr2015_state(SRC / "mmwr_nis2015.htm")
    m17 = read_stacks2017(SRC / "mmwr_nis2017_supp_table2.pdf")
    add([r for r in m15 if r["vaccine"] == "hepa_2"], "mmwr_nis2015.htm")
    add([r for r in m17 if r["vaccine"] == "hepa_2"], "mmwr_nis2017_supp_table2.pdf")
    qa.append("\n== 2. PDF extraction check: user's guide Table F.7 against the MMWR state table "
              "(MMR 1+ and DTaP 4+, 52 areas each)")
    for year, other in ((2015, m15), (2017, m17)):
        diff = [(r["state"], r["vaccine"], f7[(year, r["state"], r["vaccine"])], r["estimate"])
                for r in other if r["vaccine"] != "hepa_2"
                and f7[(year, r["state"], r["vaccine"])] != r["estimate"]]
        n = sum(1 for r in other if r["vaccine"] != "hepa_2")
        qa.append(f"{year}: {n} cells compared, {len(diff)} differ" + "".join(f"\n      {d}" for d in diff))
    qa.append("2016: no second state table obtained, Table F.7 stands alone "
              "(US row checked in sections 4 and 5)")

    # national-only rows where no state table carries the vaccine
    nat08, cap08 = mmwr_national_table(SRC / "mmwr_nis2008.htm")
    nat12, _cap12 = mmwr_national_table(SRC / "mmwr_nis2012.htm")
    nat17, cap17 = mmwr_national_table(SRC / "mmwr_nis2017.htm")
    have = {(r["year"], r["vaccine"]) for r in rows if r["state"] == "United States"}
    for nat, cap, fname in ((nat08, cap08, "mmwr_nis2008.htm"), (nat17, cap17, "mmwr_nis2017.htm")):
        for (y, vac), (est, hw, lo, hi, mark) in sorted(nat.items()):
            if (y, vac) in have or not 1995 <= y <= 2017:
                continue
            have.add((y, vac))
            flag = "national figure only, no state table with this vaccine was obtained for this year"
            if mark:
                flag += f"; mark {mark}"
            add([{"year": y, "state": "United States", "vaccine": vac, "estimate": est,
                  "ci_half_width": hw, "ci_low": lo, "ci_high": hi, "flag": flag,
                  "source_table": cap}], fname)

    # ---- sanity checks ----------------------------------------------------
    qa.append("\n== 3. Range and completeness")
    bad = [r for r in rows if r["estimate"] is not None and not 0 <= r["estimate"] <= 100]
    qa.append(f"estimates outside 0-100: {len(bad)}")
    bad = [r for r in rows if r["ci_half_width"] is not None and not 0 <= r["ci_half_width"] <= 25]
    qa.append(f"CI half-widths outside 0-25: {len(bad)}" + "".join(
        f"\n      {r['year']} {r['state']} {r['vaccine']} ±{r['ci_half_width']}" for r in bad))
    bad = [r for r in rows if r["ci_low"] is not None and not r["ci_low"] <= r["estimate"] <= r["ci_high"]]
    qa.append(f"estimates outside their own CI range: {len(bad)}")
    na = [r for r in rows if r["estimate"] is None]
    qa.append(f"cells the publisher left without a number: {len(na)}" + "".join(
        f"\n      {r['year']} {r['state']} {r['vaccine']}: {r['flag']}" for r in na))
    wide = [r for r in rows if r["ci_half_width"] is not None and r["ci_half_width"] > 10]
    qa.append(f"state cells with CI half-width above 10 points (CDC calls these possibly unreliable): {len(wide)}"
              + "".join(f"\n      {r['year']} {r['state']} {r['vaccine']} {r['estimate']}±{r['ci_half_width']}"
                        for r in wide))
    low = [r for r in rows if r["estimate"] is not None and r["vaccine"] != "hepa_2" and r["estimate"] < 65]
    qa.append(f"non-hepatitis-A estimates below 65: {len(low)}" + "".join(
        f"\n      {r['year']} {r['state']} {r['vaccine']} {r['estimate']}" for r in low))
    dup = pd.DataFrame(rows).duplicated(["year", "state", "vaccine"]).sum()
    qa.append(f"duplicate year/state/vaccine rows: {dup}")
    order = ["mmr_1", "dtp_4", "dtp_3", "polio_3", "hepa_2"]
    grid = pd.DataFrame([r for r in rows if r["state"] != "United States" and r["estimate"] is not None])
    grid = grid.pivot_table(index="year", columns="vaccine", values="state", aggfunc="nunique").reindex(
        index=range(1995, 2018), columns=order).fillna(0).astype(int)
    usg = pd.DataFrame([r for r in rows if r["state"] == "United States"]).pivot_table(
        index="year", columns="vaccine", values="estimate").reindex(index=grid.index, columns=order)
    hw = pd.DataFrame([r for r in rows if r["state"] != "United States" and r["ci_half_width"] is not None])
    hw = hw.groupby("year").ci_half_width.describe()[["min", "50%", "max"]].round(1)
    qa.append("states (of 51, counting DC) with an estimate:\n" + grid.to_string())
    qa.append("United States row:\n" + usg.to_string())
    qa.append("state 95% CI half-width, all five vaccines pooled (min, median, max):\n" + hw.to_string())

    us = {(r["year"], r["vaccine"]): r["estimate"] for r in rows if r["state"] == "United States"}
    qa.append("\n== 4. United States row against the survey's own national series "
              "(2017 user's guide, Table G.4)")
    g4 = dug_g4(SRC / "NIS-PUF17-DUG.pdf")
    diff = [(k, us.get(k), v) for k, v in sorted(g4.items()) if us.get(k) != v]
    qa.append(f"{len(g4)} cells compared, {len(diff)} differ" + "".join(
        f"\n      {k[0]} {k[1]}: table {a}, G.4 {b}" for k, a, b in diff))

    qa.append("\n== 5. United States row against the national table printed in MMWR")
    t98 = mmwr1998_text_table(SRC / "mmwr_nis1998.htm")
    for (y, vac), v in sorted(t98.items()):
        mine = us.get((y, "mmr_1" if vac == "mcv_1" else vac))
        qa.append(f"{y} {vac:8s} MMWR notice on 1998, Table 1: {v}   our table: {mine}   "
                  + ("same" if mine == v else f"differs by {round(mine - v, 1)}"))
    seen = {}
    for nat, fname in ((nat08, "mmwr_nis2008.htm"), (nat12, "mmwr_nis2012.htm"), (nat17, "mmwr_nis2017.htm")):
        for k, v in nat.items():
            seen.setdefault(k, (v[0], fname))
    diff = [(k, us.get(k), v) for k, v in sorted(seen.items()) if k in us and us[k] != v[0]]
    n = sum(1 for k in seen if k in us)
    qa.append(f"2004-2017 (MMWR reports on 2008, 2012 and 2017, Table 1): {n} cells compared, "
              f"{len(diff)} differ" + "".join(f"\n      {k}: table {a}, MMWR {b}" for k, a, b in diff))
    qa.append("1997-2003: the MMWR national tables are images (mmwr_nis2001_table1.gif, "
              "mmwr_nis2003_table1.gif); read by eye, see NOTES.md")

    rows.sort(key=lambda r: (r["year"], r["state"] != "United States", r["state"], r["vaccine"]))
    with open(OUT / "nis_state_survey_year.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=NIS_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in NIS_FIELDS})
    return rows


# ==========================================================================
# B. BUILD: national coverage before 1995
# ==========================================================================
PRE_FIELDS = ["year", "survey", "age_group", "vaccine", "estimate", "flag",
              "source_url", "source_file", "source_table"]


def words_table(page, year_x, columns, y_range, years):
    """Read a table from PDF word positions: a year in the year column, then every
    number on the same line goes to the column whose left edge it shares."""
    words = page.get_text("words")
    out = {}
    for w in words:
        if not (abs(w[0] - year_x) < 4 and re.fullmatch(r"(19\d\d)", w[4])
                and y_range[0] <= w[1] <= y_range[1]):
            continue
        year = int(w[4])
        if year not in years:
            continue
        for v in words:
            if abs(v[1] - w[1]) < 3 and v[0] > w[2] and re.fullmatch(r"\d+(\.\d)?", v[4]):
                col = [c for c, x in columns.items() if abs(v[0] - x) < 8]
                if len(col) == 1:
                    out[(year, col[0])] = v[4]
    return out


def read_simpson(path: Path):
    doc = fitz.open(path)
    p1 = next(p for p in doc if "Table 1. Vaccination coverage in children aged 1 to 4 years" in p.get_text())
    p2 = next(p for p in doc if "Table 2. USIS-reported coverage rates" in p.get_text())

    def header_x(page, names, x_min, x_max, y_max):
        xs = {}
        for w in page.get_text("words"):
            if w[4] in names and x_min <= w[0] <= x_max and w[1] <= y_max:
                xs[names[w[4]]] = w[0]
        if len(xs) != len(names):
            raise ValueError(f"table header not found: {xs}")
        return xs

    yx1 = min(w[0] for w in p1.get_text("words") if w[4] == "1959" and w[1] < 200)
    c1 = header_x(p1, {"Polio": "polio_3", "DTP": "dtp_3", "Measles": "measles", "Mumps": "mumps",
                       "Rubella": "rubella"}, yx1, 600, 90)
    t1 = words_table(p1, yx1, c1, (90, 400), range(1959, 1986))
    yx2 = min(w[0] for w in p2.get_text("words") if w[4] == "1991")
    c2 = header_x(p2, {"DTP3": "dtp_3", "Polio3": "polio_3", "Measles": "measles", "Mumps": "mumps",
                       "Rubella": "rubella"}, yx2, 300, 110)
    t2 = words_table(p2, yx2, c2, (110, 300), list(range(1979, 1986)) + [1991, 1992, 1993])
    return t1, t2


def read_hus95(path: Path):
    doc = fitz.open(path)
    text = next(p.get_text() for p in doc if "Table 54. Vaccinations of children 19–35 months" in p.get_text())
    lines = [squash(x) for x in text.split("\n")]
    title = squash(" ".join(lines[:2]))
    out, vac = {}, None
    for i, x in enumerate(lines):
        if x.startswith("DTP:"):
            vac = "dtp_3"
        elif x.startswith("Polio:"):
            vac = "polio_3"
        elif x.startswith("Measles-containing:"):
            vac = "measles_containing"
        elif re.match(r"^[A-Z][A-Za-z -]+:", x):
            vac = None
        m = re.match(r"^(199\d) [. ]+$", x)
        if m and vac and re.fullmatch(r"\d\d\.\d", lines[i + 1]):
            out[(int(m.group(1)), vac)] = lines[i + 1]     # first number after the year = Total column
    if len(out) != 9:
        raise ValueError(f"Health US 1995 Table 54: expected 9 cells, got {len(out)}")
    return out, title


def read_hus86_total(path: Path):
    """Total column of Health, United States 1986, Table 34 (scanned, OCR text layer)."""
    lines = [squash(x) for x in fitz.open(path)[0].get_text().split("\n")]
    names = [("Measles:", "measles"), ("Rubella:", "rubella"), ("clTp", "dtp_3"), ("DTP", "dtp_3"),
             ("Polio:", "polio_3"), ("Mumps:", "mumps")]
    out, vac = {}, None
    for i, x in enumerate(lines):
        if x.startswith("Respondents consulting"):
            break
        for start, v in names:
            if x.startswith(start):
                vac = v
        m = re.match(r"^(19\d\d) \.{5,}", x)
        if m and vac and re.fullmatch(r"\d\d\.\d", lines[i + 1]):
            out[(int(m.group(1)), vac)] = lines[i + 1]
    return out


def build_pre1995(qa: list[str]):
    t1, t2 = read_simpson(SRC / "simpson2001_ajpm.pdf")
    h95, h95_title = read_hus95(SRC / "hus95.pdf")
    h86 = read_hus86_total(SRC / "hus86_table34_pdfpage124.pdf")
    h78_text = squash(fitz.open(SRC / "hus78_table36_pdfpage214.pdf")[0].get_text())

    s_file = "simpson2001_ajpm.pdf"
    s_t1 = ("Simpson DM, Ezzati-Rice TM, Zell ER. Forty years and four surveys. Am J Prev Med "
            "2001;20(4S):6-14. Table 1. Vaccination coverage in children aged 1 to 4 years by antigen")
    s_t2 = ("Simpson DM, Ezzati-Rice TM, Zell ER. Forty years and four surveys. Am J Prev Med "
            "2001;20(4S):6-14. Table 2. USIS-reported coverage rates for children aged 24 to 35 months "
            "for 1979-1985, NHIS-reported coverage rates for children aged 24 to 35 months for 1991-1993")
    rows = []
    for (y, vac), v in sorted(t1.items()):
        flag = ""
        if "." not in v:
            flag = "printed as a whole number in the source"
        if (y, vac) in h86 and h86[(y, vac)] != v:
            flag = (f"Health, United States 1986, Table 34 prints {h86[(y, vac)]} for this cell; "
                    "Health, United States 1978, Table 36 prints the value used here")
        rows.append({"year": y, "survey": "USIS", "age_group": "1-4 years", "vaccine": vac,
                     "estimate": v, "flag": flag, "source_file": s_file, "source_table": s_t1})
    for (y, vac), v in sorted(t2.items()):
        if y <= 1985:
            rows.append({"year": y, "survey": "USIS", "age_group": "24-35 months", "vaccine": vac,
                         "estimate": v, "flag": "", "source_file": s_file, "source_table": s_t2})
        elif y == 1991:
            rows.append({"year": y, "survey": "NHIS", "age_group": "24-35 months", "vaccine": vac,
                         "estimate": v, "source_file": s_file, "source_table": s_t2,
                         "flag": "age group as labeled by Simpson et al.; Health, United States prints the "
                                 "same 1992 and 1993 figures for children 19-35 months, so the label may "
                                 "be loose"})
    for (y, vac), v in sorted(h95.items()):
        rows.append({"year": y, "survey": "NHIS", "age_group": "19-35 months", "vaccine": vac,
                     "estimate": v, "flag": "", "source_file": "hus95.pdf",
                     "source_table": "Health, United States, 1995. " + h95_title + " (Total column)"})
    for r in rows:
        r["source_url"] = SOURCE_URL[r["source_file"]]
        if not 0 <= float(r["estimate"]) <= 100:
            raise ValueError(f"out of range: {r}")
    rows.sort(key=lambda r: (r["survey"] != "USIS", r["age_group"], r["vaccine"], r["year"]))
    with open(OUT / "national_pre1995.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PRE_FIELDS)
        w.writeheader()
        w.writerows(rows)

    qa.append("\n== 6. Before 1995: Simpson et al. Table 1 (children 1-4, USIS) against Health, United States")
    df = pd.DataFrame(rows)
    for (survey, age), g in df.groupby(["survey", "age_group"], sort=False):
        qa.append(f"{survey}, {age}: " + ", ".join(
            f"{v} {gg.year.min()}-{gg.year.max()} ({len(gg)})" for v, gg in g.groupby("vaccine")))
    same = [(k, v) for k, v in sorted(h86.items()) if t1.get(k) == v]
    diff = [(k, t1.get(k), v) for k, v in sorted(h86.items()) if t1.get(k) != v]
    qa.append(f"Health US 1986 Table 34, Total column (1970, 1976, 1983-85): {len(h86)} cells read, "
              f"{len(same)} equal, {len(diff)} differ" + "".join(
                  f"\n      {k}: Simpson {a}, Health US 1986 {b}" for k, a, b in diff))
    for vac in ("measles", "rubella", "dtp_3", "polio_3", "mumps"):
        seq = [t1[(y, vac)] for y in range(1970, 1977) if (y, vac) in t1]
        found = [v in h78_text for v in seq]
        qa.append(f"Health US 1978 Table 36, {vac} 1970-76: {sum(found)} of {len(seq)} Simpson values "
                  f"present in the page's OCR text"
                  + ("" if all(found) else f"   not found: {[v for v, ok in zip(seq, found) if not ok]}"))
    sim = {k: v for k, v in t2.items() if k[0] in (1992, 1993)}
    h = {(y, "measles" if v == "measles_containing" else v): x for (y, v), x in h95.items()}
    diff = [(k, v, h.get(k)) for k, v in sorted(sim.items()) if h.get(k) != v]
    qa.append(f"NHIS 1992-93: Simpson Table 2 against Health US 1995 Table 54: {len(sim)} cells, "
              f"{len(diff)} differ {diff if diff else ''}")
    return rows


# ==========================================================================
# C. BUILD: licensure years
# ==========================================================================
# (vaccine key, source file, regex with the year as group 'y' and an optional
#  full date as group 'd', what the year means)
LICENSURE_RULES = [
    ("polio_inactivated_salk", "lic_pinkbook_polio.html",
     r"Inactivated poliovirus \(IPV\) vaccine was licensed for use in (?P<y>\d{4})", "licensed"),
    ("polio_oral_sabin", "lic_pinkbook_polio.html",
     r"In (?P<y>\d{4}), type 1 and 2 monovalent oral poliovirus \(mOPV\) vaccines were licensed[^.]*",
     "first oral vaccines licensed (monovalent types 1 and 2)"),
    ("polio_oral_sabin_trivalent", "lic_pinkbook_polio.html",
     r"In \d{4}, type 1 and 2 monovalent oral poliovirus[^.]*trivalent OPV \(tOPV\) vaccine in (?P<y>\d{4})",
     "trivalent oral vaccine licensed"),
    ("measles", "lic_pinkbook_measles.html",
     r"In (?P<y>\d{4}), both an inactivated \(.killed.\) and a live, attenuated \(Edmonston B strain\) "
     r"measles vaccine were licensed for use in the United States", "licensed"),
    ("mumps", "lic_pinkbook_mumps.html",
     r"The live, attenuated mumps vaccine \(Jeryl Lynn strain\) was licensed for use in the United States "
     r"in (?P<y>\d{4})", "licensed"),
    ("rubella", "lic_pinkbook_rubella.html",
     r"The first rubella vaccines were licensed in (?P<y>\d{4})", "licensed"),
    ("mmr_combined", "lic_pinkbook_measles.html",
     r"In (?P<y>\d{4}), a combined measles, mumps, and rubella \(MMR\) vaccine was licensed for use in the "
     r"United States", "licensed"),
    ("pertussis_whole_cell", "lic_pinkbook_pertussis.html",
     r"Whole-cell pertussis vaccines were first licensed in the United States in (?P<y>\d{4})[^.]*",
     "licensed (pertussis vaccine alone)"),
    ("dtp_whole_cell", "lic_pinkbook_pertussis.html",
     r"Whole-cell pertussis vaccines were first licensed in the United States in \d{4} and were available "
     r"as a combined vaccine with diphtheria and tetanus toxoids \(as DTP\) in (?P<y>\d{4})",
     "combined DTP became available; the source does not use the word licensed for this year"),
    ("dtap_acellular", "lic_mmwr_dtap_1992.htm",
     r"On (?P<d>December 17, (?P<y>1991)), the FDA licensed one D[Tt]a[Pp] vaccine for use as the fourth "
     r"and fifth doses of the recommended DTP series", "licensed for the fourth and fifth doses only"),
    ("dtap_acellular_infants", "lic_mmwr_dtap_infants_1996.htm",
     r"On (?P<d>July 31, (?P<y>1996)), the Food and Drug Administration licensed[^.]*\.[^.]*",
     "first acellular vaccine licensed for the first doses, in infants"),
    ("hepatitis_a", "lic_mmwr_hepa_1995.htm",
     r"In (?P<d>February (?P<y>1995)), Havrix[^,]*,[^.]*was licensed by the Food and Drug Administration"
     r"[^.]*", "licensed (month stated, no day)"),
    ("hepatitis_a", "lic_pinkbook_hepatitis_a.html",
     r"Hepatitis A \(HepA\) vaccines were first licensed for use in the United States in (?P<y>\d{4})",
     "licensed"),
    ("diphtheria_toxoid", "lic_mmwr_achievements_1999.htm",
     r"Diphtheria\* (?P<y>\d{4})\+", "year the vaccine was developed (first published results of use), "
     "per the table legend; the source gives no licensure year for diphtheria toxoid"),
    ("polio_inactivated_salk", "lic_mmwr_achievements_1999.htm",
     r"Polio vaccine was licensed in the United States in (?P<y>\d{4})", "licensed"),
    ("measles", "lic_mmwr_achievements_1999.htm",
     r"Measles vaccine was licensed in the United States in (?P<y>\d{4})", "licensed"),
    ("mumps", "lic_mmwr_achievements_1999.htm", r"Mumps\* (?P<y>\d{4})&", "licensed, per the table legend"),
    ("rubella", "lic_mmwr_achievements_1999.htm", r"Rubella\* (?P<y>\d{4})&", "licensed, per the table legend"),
    ("hepatitis_a", "lic_mmwr_achievements_1999.htm", r"Hepatitis A (?P<y>\d{4})&",
     "licensed, per the table legend"),
]
LIC_FIELDS = ["vaccine", "year", "date_if_stated", "source_title", "source_url", "source_file",
              "what_the_year_means", "source_quote"]


def build_licensure(qa: list[str]):
    rows, cache = [], {}
    for vac, fname, pat, meaning in LICENSURE_RULES:
        if fname not in cache:
            soup = BeautifulSoup((SRC / fname).read_text(errors="replace"), "lxml")
            cache[fname] = (squash(soup.title.get_text(" ")), squash(soup.get_text(" ")))
        title, text = cache[fname]
        m = re.search(pat, text)
        if not m:
            raise ValueError(f"licensure sentence not found for {vac} in {fname}")
        rows.append({"vaccine": vac, "year": int(m.group("y")),
                     "date_if_stated": m.groupdict().get("d") or "", "source_title": title,
                     "source_url": SOURCE_URL[fname], "source_file": fname,
                     "what_the_year_means": meaning, "source_quote": squash(m.group(0))})
    if "+ Vaccine developed (i.e., first published results of vaccine usage). & Vaccine licensed for use " \
       "in United States" not in cache["lic_mmwr_achievements_1999.htm"][1]:
        raise ValueError("legend of the MMWR 1999 table has changed")
    with open(OUT / "licensure.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LIC_FIELDS)
        w.writeheader()
        w.writerows(rows)
    qa.append("\n== 7. Licensure: do the sources agree on the year?")
    df = pd.DataFrame(rows)
    for vac, g in df.groupby("vaccine", sort=False):
        qa.append(f"{vac}: {sorted(set(g.year))} from {len(g)} source(s)")
    return rows


def main():
    fetch_all()
    qa = ["QA log written by scripts/04b_fetch_vax_history.py. Do not edit by hand.\n"]
    build_nis(qa)
    build_pre1995(qa)
    build_licensure(qa)
    (OUT / "qa_checks.txt").write_text("\n".join(qa) + "\n")
    print("\n".join(qa))


if __name__ == "__main__":
    main()
