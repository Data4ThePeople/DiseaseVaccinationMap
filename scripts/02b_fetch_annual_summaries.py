#!/usr/bin/env python3
"""02b_fetch_annual_summaries.py

Final annual reported case counts by state from official CDC annual tables.

Sources (all saved under data/raw/bridge/src/):
  1993-2015  MMWR "Summary of Notifiable Diseases" annual issues, Table 2
             ("Reported cases of notifiable diseases, by geographic division
             and area"). Primary extraction is from the text layer of the
             issue PDF. For 2007-2015 the HTML version of the same issue is
             parsed independently and compared cell by cell.
  2016-2023  NNDSS Annual Tables, Table 2 parts, tab-delimited text files on
             CDC Stacks (stacks.cdc.gov).

Outputs (data/raw/bridge/):
  annual_state_cases.csv      the deliverable (50 states + DC)
  annual_area_cases_all.csv   every area row as printed (US total, regions,
                              New York City / upstate split, territories)
  checks_state_sum_vs_us.csv  sum of states vs the table's own US total row
  checks_html_vs_pdf.csv      2007-2015 cell by cell HTML vs PDF comparison
  checks_owid_measles.csv     measles vs Our World in Data transcription
  checks_marks.csv            mark definitions found in each source
  checks_column_map.csv       which printed column was read for each disease

Re-runnable: files already present in src/ are not downloaded again.

Needs: requests, pandas, pymupdf (fitz), beautifulsoup4, lxml.
"""
import csv
import io
import os
import re
import sys
import time
from collections import defaultdict
from urllib.parse import urlparse

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE = os.path.join(ROOT, "data", "raw", "bridge")
SRC = os.path.join(BRIDGE, "src")
UA = "Mozilla/5.0 (D4TP research; eric@data4thepeople.com)"
OWID_URL = "https://snapshots.owid.io/42/5183f3594159428637846963fe915c"

DISEASES = ["measles", "measles_indigenous", "measles_imported", "pertussis",
            "mumps", "rubella", "hepatitis_a", "diphtheria", "polio_paralytic"]

# --------------------------------------------------------------------------
# Source catalogue
# --------------------------------------------------------------------------
# MMWR Summary of Notifiable Diseases: data year -> issue code.
MMWR_ISSUES = {
    1993: "mm4253", 1994: "mm4353", 1995: "mm4453", 1996: "mm4553",
    1997: "mm4654", 1998: "mm4753", 1999: "mm4853", 2000: "mm4953",
    2001: "mm5053", 2002: "mm5153", 2003: "mm5254", 2004: "mm5353",
    2005: "mm5453", 2006: "mm5553", 2007: "mm5653", 2008: "mm5754",
    2009: "mm5853", 2010: "mm5953", 2011: "mm6053", 2012: "mm6153",
    2013: "mm6253", 2014: "mm6354", 2015: "mm6453",
}


def mmwr_pdf_url(year):
    code = MMWR_ISSUES[year]
    if year >= 2014:
        return "https://www.cdc.gov/mmwr/volumes/%s/wr/pdfs/%s.pdf" % (code[2:4], code)
    return "https://www.cdc.gov/mmwr/PDF/wk/%s.pdf" % code


def mmwr_html_url(year):
    code = MMWR_ISSUES[year]
    if year >= 2014:
        return "https://www.cdc.gov/mmwr/volumes/%s/wr/%sa1.htm" % (code[2:4], code)
    return "https://www.cdc.gov/mmwr/preview/mmwrhtml/%sa1.htm" % code


HTML_YEARS = range(2007, 2016)   # years whose HTML carries real tables

# NNDSS Annual Tables, Table 2 parts that carry the diseases wanted here.
# Record ids were read from the CDC Stacks NNDSS collection listing
# (https://stacks.cdc.gov/cbrowse?pid=cdc:49375&parentId=cdc:49375, genre
# "Annual Report" / "Annual Tables"). Every file states its own table letter
# and year in its first line and the parser reads both from there.
#   ("stacks_txt", record)      tab-delimited text supporting file (DS2 or DS3)
#   ("stacks_pdf", record)      2023: Stacks carries the PDF only
#   ("wayback_txt", letter, ts) 2017: the Stacks records for the 2017 Table 2
#       parts redirect to the 2018 records, so the 2017 files are taken from
#       Internet Archive captures of the CDC WONDER originals
#       (wonder.cdc.gov/nndss/static/2017/annual/2017-table2X.txt).
NNDSS_SOURCES = {
    2016: [("stacks_txt", r) for r in (49381, 49383, 49385, 49386, 49387, 49388)],
    2017: [("wayback_txt", "e", "20250109233529"), ("wayback_txt", "g", "20241231182110"),
           ("wayback_txt", "i", "20250110024805"), ("wayback_txt", "j", "20250108105159"),
           ("wayback_txt", "k", "20250104211127"), ("wayback_txt", "l", "20250103192204")],
    2018: [("stacks_txt", r) for r in (82388, 82390, 82392, 82393, 82394, 82395)],
    2019: [("stacks_txt", r) for r in (106480, 106482, 106485, 106486, 106487, 106488)],
    2020: [("stacks_txt", r) for r in (175634, 175636, 175639, 175640, 175641, 175642)],
    2021: [("stacks_txt", r) for r in (175661, 175663, 175666, 175667, 175668, 175669)],
    2022: [("stacks_txt", r) for r in (175688, 175690, 175693, 175694, 175695, 175696)],
    2023: [("stacks_pdf", r) for r in (251104, 251106, 251109, 251110, 251111, 251112)],
}


def nndss_source(spec):
    """-> (kind, list of (url, filename) candidates; the first that exists or downloads is used)"""
    kind = spec[0]
    if kind == "stacks_txt":
        r = spec[1]
        return kind, [("https://stacks.cdc.gov/view/cdc/%d/cdc_%d_DS%d.txt" % (r, r, n),
                       "stacks_%d_DS%d.txt" % (r, n)) for n in (2, 3)]
    if kind == "stacks_pdf":
        r = spec[1]
        return kind, [("https://stacks.cdc.gov/view/cdc/%d/cdc_%d_DS1.pdf" % (r, r),
                       "stacks_%d_DS1.pdf" % r)]
    letter, ts = spec[1], spec[2]
    return kind, [("https://web.archive.org/web/%sid_/https://wonder.cdc.gov/nndss/static/2017/"
                   "annual/2017-table2%s.txt" % (ts, letter),
                   "wonder_2017-table2%s_wayback_%s.txt" % (letter, ts))]


def nndss_local(spec, download=False):
    kind, cands = nndss_source(spec)
    for url, fname in cands:
        if os.path.exists(os.path.join(SRC, fname)):
            return kind, url, fname
    if download:
        for url, fname in cands:
            if fetch(url, fname, is_pdf if kind == "stacks_pdf" else is_nndss_txt):
                return kind, url, fname
    return kind, None, None


# --------------------------------------------------------------------------
# Polite downloader
# --------------------------------------------------------------------------
_last_hit = {}
HOST_DELAY = {"stacks.cdc.gov": 10.0,    # robots.txt asks for Crawl-delay: 10
              "web.archive.org": 5.0}
DEFAULT_DELAY = 2.0
_session = None


def fetch(url, fname, validate=None):
    """Download url to src/fname unless it is already there. Returns path or None."""
    global _session
    path = os.path.join(SRC, fname)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = UA
    host = urlparse(url).netloc
    wait = HOST_DELAY.get(host, DEFAULT_DELAY) - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    try:
        r = _session.get(url, timeout=120, allow_redirects=True)
    except requests.RequestException as e:
        print("  download failed: %s (%s)" % (url, e))
        return None
    finally:
        _last_hit[host] = time.time()
    if r.status_code != 200 or (validate and not validate(r.content)):
        print("  download rejected: %s (HTTP %s, %d bytes)" % (url, r.status_code, len(r.content)))
        return None
    with open(path, "wb") as f:
        f.write(r.content)
    print("  downloaded %s (%d bytes)" % (fname, len(r.content)))
    return path


def is_pdf(b):
    return b[:5] == b"%PDF-"


def is_html_with_tables(b):
    return b"<table" in b.lower() and b"United States" in b


def is_nndss_txt(b):
    return b"tab delimited data" in b[:20000]


def download_all():
    os.makedirs(SRC, exist_ok=True)
    for year in sorted(MMWR_ISSUES):
        fetch(mmwr_pdf_url(year), MMWR_ISSUES[year] + ".pdf", is_pdf)
    for year in HTML_YEARS:
        fetch(mmwr_html_url(year), MMWR_ISSUES[year] + "a1.htm", is_html_with_tables)
    for year in sorted(NNDSS_SOURCES):
        for spec in NNDSS_SOURCES[year]:
            nndss_local(spec, download=True)
    for year in sorted(SCAN_ISSUES):
        fetch(scan_url(year), scan_file(year), is_pdf)
    fetch(OWID_URL, "owid_measles_states_crosscheck_only.csv",
          lambda b: b"year" in b[:500].lower())


# --------------------------------------------------------------------------
# Areas
# --------------------------------------------------------------------------
STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
          "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
          "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
          "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
          "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
          "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
          "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
          "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
          "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
          "Wisconsin", "Wyoming"]

NY_UP = "New York (excluding New York City)"
NY_CITY = "New York City"
US = "United States"


def _key(s):
    return re.sub(r"[^a-z]", "", s.lower())


AREA_KEYS = {_key(s): s for s in STATES}
AREA_KEYS.pop("newyork")
# The old MMWR abbreviations.
for abbr, full in {
    "N.H.": "New Hampshire", "Vt.": "Vermont", "Mass.": "Massachusetts",
    "R.I.": "Rhode Island", "Conn.": "Connecticut", "N.J.": "New Jersey",
    "Pa.": "Pennsylvania", "Ind.": "Indiana", "Ill.": "Illinois",
    "Mich.": "Michigan", "Wis.": "Wisconsin", "Minn.": "Minnesota",
    "Mo.": "Missouri", "N. Dak.": "North Dakota", "S. Dak.": "South Dakota",
    "Nebr.": "Nebraska", "Kans.": "Kansas", "Del.": "Delaware",
    "Md.": "Maryland", "D.C.": "District of Columbia", "Va.": "Virginia",
    "W. Va.": "West Virginia", "N.C.": "North Carolina",
    "S.C.": "South Carolina", "Ga.": "Georgia", "Fla.": "Florida",
    "Ky.": "Kentucky", "Tenn.": "Tennessee", "Ala.": "Alabama",
    "Miss.": "Mississippi", "Ark.": "Arkansas", "La.": "Louisiana",
    "Okla.": "Oklahoma", "Tex.": "Texas", "Mont.": "Montana", "Wyo.": "Wyoming",
    "Colo.": "Colorado", "N. Mex.": "New Mexico", "Ariz.": "Arizona",
    "Nev.": "Nevada", "Wash.": "Washington", "Oreg.": "Oregon",
    "Calif.": "California",
}.items():
    AREA_KEYS[_key(abbr)] = full
for k in ["upstateny", "nyexclnyc", "newyorkupstate", "newyorkexcludingnewyorkcity",
          "newyorkexclnyc", "upstatenewyork"]:
    AREA_KEYS[k] = NY_UP
for k in ["nycity", "nyc", "newyorkcity"]:
    AREA_KEYS[k] = NY_CITY
for k in ["unitedstates", "usresidentsexcludingusterritories"]:
    AREA_KEYS[k] = US
OTHER_AREAS = {
    "newengland": "New England", "midatlantic": "Middle Atlantic",
    "middleatlantic": "Middle Atlantic", "encentral": "East North Central",
    "eastnorthcentral": "East North Central", "wncentral": "West North Central",
    "westnorthcentral": "West North Central", "satlantic": "South Atlantic",
    "southatlantic": "South Atlantic", "escentral": "East South Central",
    "eastsouthcentral": "East South Central", "wscentral": "West South Central",
    "westsouthcentral": "West South Central", "mountain": "Mountain",
    "pacific": "Pacific", "guam": "Guam", "pr": "Puerto Rico",
    "puertorico": "Puerto Rico", "vi": "U.S. Virgin Islands",
    "virginislands": "U.S. Virgin Islands", "usvirginislands": "U.S. Virgin Islands",
    "amersamoa": "American Samoa", "americansamoa": "American Samoa",
    "cnmi": "Northern Mariana Islands", "territories": "Territories",
    "usterritories": "U.S. Territories",
    "commonwealthofnorthernmarianaislands": "Northern Mariana Islands",
    "northernmarianaislands": "Northern Mariana Islands",
    "nonusresidents": "Non-U.S. Residents", "total": "Total (incl. territories)",
    "pacifictrustterritory": "Pacific Trust Territory",
}
AREA_KEYS.update(OTHER_AREAS)


def area_of(label):
    return AREA_KEYS.get(_key(label))


# --------------------------------------------------------------------------
# Cells
# --------------------------------------------------------------------------
DASHES = "-–—−\u0097"
FOOT = "*†‡§¶#"
CELL_RE = re.compile(
    r"^(?:(\d{1,3}(?:,\s?\d{3})+|\d+)|([%s]+|N|U|NA|NN|NR|NP|NC))\s*([%s,]*)$" % (DASHES, FOOT))
SYM_RE = re.compile(r"^[%s,]+$" % FOOT)


def parse_cell(raw):
    """raw cell text -> (number or None, mark, footnote symbols). mark '-' is any dash."""
    raw = raw.replace("\xa0", " ").strip()
    if raw == "":
        return None, "blank", ""
    m = CELL_RE.match(raw)
    if not m:
        return None, raw, ""
    num, mark, sym = m.groups()
    sym = sym.replace(",", "")
    if num is not None:
        return int(re.sub(r"[,\s]", "", num)), "", sym
    if mark[0] in DASHES:
        mark = "-"
    return None, mark, sym


# --------------------------------------------------------------------------
# Column header -> disease
# --------------------------------------------------------------------------
def classify_columns(texts, page_has_hepatitis=True):
    """texts: header text of each data column, left to right.
    Returns {disease: column index}."""
    low = [re.sub(r"\s+", " ", t.lower()) for t in texts]
    out = {}

    def put(d, i):
        if d in out and out[d] != i:
            raise ValueError("two columns for %s: %r and %r" % (d, texts[out[d]], texts[i]))
        out[d] = i

    for i, t in enumerate(low):
        toks = [x.strip(FOOT + ",.;:()") for x in re.split(r"[ |]+", texts[i])]
        if "indigenous" in t:
            put("measles_indigenous", i)
        elif "imported" in t and "malaria" not in t:
            put("measles_imported", i)
        if "mumps" in t:
            put("mumps", i)
        if "pertussis" in t:
            put("pertussis", i)
        if "diphtheria" in t:
            put("diphtheria", i)
        if "rubella" in t and "cong" not in t and "syndrome" not in t:
            put("rubella", i)
        if "paralytic" in t and "nonparalytic" not in t and "non-paralytic" not in t:
            put("polio_paralytic", i)
        if page_has_hepatitis and "influenza" not in t and "serogroup" not in t:
            raw_toks = re.split(r"[ |]+", texts[i])
            if "A" in toks and "non-a" not in t:
                # "A" alone, "Hepatitis A", or "A, acute"; not "B", "C"
                if any(x in ("A", "A,") or x.strip(FOOT) == "A" for x in raw_toks):
                    if not re.search(r"\bhepatitis b\b|\bb, |\bc, ", t):
                        put("hepatitis_a", i)
    if "measles_indigenous" in out and "measles_imported" in out:
        lo = min(out["measles_indigenous"], out["measles_imported"])
        hi = max(out["measles_indigenous"], out["measles_imported"])
        cand = [k for k in (lo - 1, hi + 1) if 0 <= k < len(low) and "total" in low[k].split()]
        if hi - lo == 1 and len(cand) == 1:
            put("measles", cand[0])
        elif len(cand) > 1:
            raise ValueError("two possible measles total columns")
    elif "measles_indigenous" not in out and "measles_imported" not in out:
        for i, t in enumerate(low):
            if "measles" in t:
                put("measles", i)
    return out


# --------------------------------------------------------------------------
# MMWR PDF parser
# --------------------------------------------------------------------------
def pdf_lines(page, tol=2.5):
    words = page.get_text("words")
    words = sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    lines, cur, cy = [], [], None
    for w in words:
        y = (w[1] + w[3]) / 2
        if cy is None or abs(y - cy) > tol:
            if cur:
                lines.append(cur)
            cur, cy = [w], y
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return [sorted(l, key=lambda w: w[0]) for l in lines]


def split_row(line):
    """A line of words -> (label, [(text, x0, x1), ...]) taking the longest
    run of value-like tokens at the right end as the values."""
    toks = []
    for w in line:
        t = w[4]
        if SYM_RE.match(t) and toks:
            toks[-1] = (toks[-1][0] + t, toks[-1][1], toks[-1][2])   # "3 †" -> "3†"
        else:
            toks.append((t, w[0], w[2]))
    k = len(toks)
    while k > 0 and CELL_RE.match(toks[k - 1][0]):
        k -= 1
    label = " ".join(t[0] for t in toks[:k])
    return label, toks[k:]


MARK_DEF_RE = re.compile(
    r"^\s*(NA|NN|NR|NP|NC|N|U|[%s]{1,3})\s*[:=]\s*(.{4,220})$" % DASHES)
_PHRASE = (r"(no reported cases|not notifiable|not reportable|unavailable|"
           r"data not available|not available)")
_MARK = r"(NA|NN|N|U|[%s]{1,3})" % DASHES
_DEF_A = re.compile(r"(?<![A-Za-z.])%s\s*[:=]\s*%s" % (_MARK, _PHRASE), re.I)
_DEF_B = re.compile(r"%s\)?\s*\.{3,}\s*%s\s*$" % (_PHRASE, _MARK), re.I)
_DEF_C = re.compile(r"^%s$" % _MARK)


def find_mark_defs(pages):
    """pages: list of page texts. Returns {mark: 'definition as printed (p.N)'}.
    Three layouts occur: 'N: Not notifiable' / 'N = not reportable' footnotes,
    'No reported cases ....... -' dotted lists, and a symbol on one line with
    its meaning on the next ('Abbreviations and Symbols Used in Tables')."""
    out = {}

    def put(mark, text, pno):
        mark = mark.strip()
        if mark[0] in DASHES:
            mark = "-"
        else:
            mark = mark.upper()
        out.setdefault(mark, "%s (p.%d)" % (re.sub(r"\s+", " ", text).strip(), pno))

    for pno, text in enumerate(pages, start=1):
        lines = [l.strip() for l in text.splitlines()]
        lines = [l for l in lines if l]
        for i, l in enumerate(lines):
            for m in _DEF_A.finditer(l):
                put(m.group(1), m.group(2), pno)
            m = _DEF_B.search(l)
            if m:
                prev = lines[i - 1] + " " if i and "...." not in lines[i - 1] and len(lines[i - 1]) < 60 \
                    and "not required" in lines[i - 1] else ""
                put(m.group(2), prev + re.sub(r"\s*\.{3,}.*$", "", l), pno)
            if _DEF_C.match(l) and i + 1 < len(lines) and re.match(_PHRASE, lines[i + 1], re.I):
                nxt = lines[i + 1]
                if nxt.count("(") > nxt.count(")") and i + 2 < len(lines) and len(lines[i + 2]) < 80:
                    nxt += " " + lines[i + 2]
                put(l, nxt, pno)
    return out


def parse_mmwr_pdf(year):
    import fitz
    code = MMWR_ISSUES[year]
    fname = code + ".pdf"
    path = os.path.join(SRC, fname)
    if not os.path.exists(path):
        return None
    doc = fitz.open(path)
    res = {"cells": [], "marks": {}, "colmap": [], "warn": [], "text": []}
    seen = {}
    last = None     # the table read on the previous page, for two-page tables
    for pno, page in enumerate(doc, start=1):
        text = page.get_text()
        res["text"].append(text)
        if not re.search(r"Indigenous|Mumps|Pertussis|Rubella|Diphtheria|aralytic|Hepatitis|Measles",
                         text):
            last = None
            continue
        lines = pdf_lines(page)
        rows, us_idx = [], None
        for li, line in enumerate(lines):
            label, vals = split_row(line)
            area = area_of(label) if label and vals else None
            rows.append((label, vals, area))
            if area == US and us_idx is None and len(vals) >= 2:
                us_idx = li
        letter = re.search(r"TABLE 2([a-z])\.", text)
        letter = letter.group(1) if letter else ""
        if us_idx is None:
            # second page of a table that started on the previous page (2014, 2015)
            if last and last["pno"] == pno - 1 and last["letter"] == letter and letter:
                for (label, vals, area) in rows:
                    if area is None or area in last["areas"]:
                        continue
                    if len(vals) != last["ncol"]:
                        res["warn"].append("p%d: continuation row %r has %d values, expected %d" %
                                           (pno, label, len(vals), last["ncol"]))
                        continue
                    for d, j in last["cmap"].items():
                        if seen.get(d) != last["pno"]:
                            continue
                        res["cells"].append((area, label, d, vals[j][0],
                                             "Table 2%s, PDF pages %d-%d, column \"%s\"" %
                                             (letter, last["pno"], pno, last["texts"][j])))
            last = None
            continue
        last = None
        nstate = sum(1 for (_, _, a) in rows if a in STATES or a in (NY_UP, NY_CITY))
        if nstate < 40:
            continue
        us_vals = rows[us_idx][1]
        ncol = len(us_vals)
        centers = [(v[1] + v[2]) / 2 for v in us_vals]
        anchors = [v[2] for v in us_vals]
        us_y = (lines[us_idx][0][1] + lines[us_idx][0][3]) / 2
        # header words: everything printed just above the US row except the
        # title lines. (The 1999 issue stores the header after the body in the
        # text stream, but its coordinates are still above the US row.)
        texts = [[] for _ in range(ncol)]
        hdr_words = []
        for line in lines:
            ly = (line[0][1] + line[0][3]) / 2
            s = " ".join(w[4] for w in line)
            if re.search(r"(?i)reported cases|MMWR|United States,|\bVol\.|territories, \d{4}|"
                         r"NOTIFIABLE DISEASES|sion and area|Morbidity and Mortality|Health and Human", s):
                continue
            if us_y - 80 < ly < us_y - 2.5:
                hdr_words.extend(line)
        hdr_words.sort(key=lambda w: (round(w[1]), w[0]))
        for w in hdr_words:
            if w[4] == "Area":
                continue
            c = (w[0] + w[2]) / 2
            j = min(range(ncol), key=lambda j: abs(c - centers[j]))
            texts[j].append(w[4])
        texts = [" ".join(t) for t in texts]
        full_hdr = " ".join(w[4] for w in hdr_words)
        try:
            cmap = classify_columns(texts, "hepatitis" in full_hdr.lower())
        except ValueError as e:
            res["warn"].append("p%d: %s" % (pno, e))
            continue
        if not cmap:
            continue
        tname = "Table 2%s" % letter
        areas_here = set()
        for d, j in cmap.items():
            if d in seen:
                res["warn"].append("p%d: %s already read on p%d; kept first" % (pno, d, seen[d]))
                continue
            seen[d] = pno
            res["colmap"].append((d, pno, texts[j], us_vals[j][0]))
            for (label, vals, area) in rows:
                if area is None:
                    continue
                if len(vals) == ncol:
                    raw = vals[j][0]
                else:
                    near = [v for v in vals if abs(v[2] - anchors[j]) < 6]
                    res["warn"].append("p%d: row %r has %d values, expected %d" %
                                       (pno, label, len(vals), ncol))
                    if len(near) > 1:
                        continue
                    raw = near[0][0] if near else ""     # nothing printed in this cell
                areas_here.add(area)
                res["cells"].append((area, label, d, raw, "%s, PDF page %d, column \"%s\"" %
                                     (tname, pno, texts[j])))
        last = {"pno": pno, "letter": letter, "ncol": ncol, "cmap": cmap, "texts": texts,
                "areas": areas_here}
    res["marks"] = find_mark_defs(res["text"])
    res["url"] = mmwr_pdf_url(year)
    res["file"] = fname
    return res


# --------------------------------------------------------------------------
# Scanned annual summaries 1980-1992 (CDC Stacks PDFs with an OCR text layer)
# --------------------------------------------------------------------------
# Only measles and pertussis are read from these. Nothing is corrected by
# hand or by guesswork: a disease-year is used only if every state cell reads
# as a number or a defined mark, the states of every geographic division add
# up to the printed division row, the divisions add up to the printed United
# States row, and the states add up to the printed United States row.
SCAN_ISSUES = {
    1992: 36063, 1991: 36010, 1990: 35905, 1989: 35853, 1988: 35958, 1987: 35629,
    1986: 35496, 1985: 35429, 1984: 35267, 1983: 35188, 1982: 35066, 1981: 1307,
    1980: 1484,
}
SCAN_DISEASES = ("measles", "measles_indigenous", "measles_imported", "pertussis")
# OCR spellings of area labels seen in the scans (labels only, never numbers)
SCAN_LABEL_ALIASES = {"rl": "Rhode Island", "iii": "Illinois", "lll": "Illinois",
                      "ili": "Illinois", "lii": "Illinois", "iil": "Illinois"}
DIVISIONS = {
    "New England": ["Maine", "New Hampshire", "Vermont", "Massachusetts", "Rhode Island",
                    "Connecticut"],
    "Middle Atlantic": [NY_UP, NY_CITY, "New Jersey", "Pennsylvania"],
    "East North Central": ["Ohio", "Indiana", "Illinois", "Michigan", "Wisconsin"],
    "West North Central": ["Minnesota", "Iowa", "Missouri", "North Dakota", "South Dakota",
                           "Nebraska", "Kansas"],
    "South Atlantic": ["Delaware", "Maryland", "District of Columbia", "Virginia",
                       "West Virginia", "North Carolina", "South Carolina", "Georgia", "Florida"],
    "East South Central": ["Kentucky", "Tennessee", "Alabama", "Mississippi"],
    "West South Central": ["Arkansas", "Louisiana", "Oklahoma", "Texas"],
    "Mountain": ["Montana", "Idaho", "Wyoming", "Colorado", "New Mexico", "Arizona", "Utah",
                 "Nevada"],
    "Pacific": ["Washington", "Oregon", "California", "Alaska", "Hawaii"],
}


def scan_url(year):
    r = SCAN_ISSUES[year]
    return "https://stacks.cdc.gov/view/cdc/%d/cdc_%d_DS1.pdf" % (r, r)


def scan_file(year):
    return "stacks_%d_DS1.pdf" % SCAN_ISSUES[year]


def scan_area(label):
    k = _key(label)
    return AREA_KEYS.get(k) or SCAN_LABEL_ALIASES.get(k)


def deskewed_lines(page, tol=2.6):
    """Scans are slightly rotated, which breaks a table row into two text
    lines. Try a range of small slopes and keep the one that packs the words
    into the fewest lines."""
    words = page.get_text("words")
    best = None
    for k in range(-15, 16):
        slope = k * 0.002
        ws = sorted(words, key=lambda w: ((w[1] + w[3]) / 2 - slope * w[0], w[0]))
        lines, cur, cy = [], [], None
        for w in ws:
            y = (w[1] + w[3]) / 2 - slope * w[0]
            if cy is None or abs(y - cy) > tol:
                if cur:
                    lines.append(cur)
                cur, cy = [w], y
            else:
                cur.append(w)
        if cur:
            lines.append(cur)
        if best is None or len(lines) < len(best[1]) or (len(lines) == len(best[1]) and abs(slope) < abs(best[0])):
            best = (slope, lines)
    return best[0], [sorted(l, key=lambda w: w[0]) for l in best[1]]


def merge_close(words, gap=5.0):
    """Join OCR fragments of one number ('2' ',4' '1' '0' -> '2,410')."""
    out = []
    for w in words:
        if out and w[0] - out[-1][2] < gap:
            p_ = out[-1]
            out[-1] = (p_[0], min(p_[1], w[1]), w[2], max(p_[3], w[3]), p_[4] + w[4])
        else:
            out.append(tuple(w[:5]))
    return out


def parse_scan_pdf(year):
    """-> dict with 'cells' (area, label, disease, raw, table), 'colmap', 'warn', 'text'.
    Column membership is decided by position only: a token belongs to the
    column whose span (taken from the United States row) contains its centre."""
    import fitz
    path = os.path.join(SRC, scan_file(year))
    if not os.path.exists(path):
        return None
    doc = fitz.open(path)
    res = {"cells": [], "colmap": [], "warn": [], "text": [], "url": scan_url(year),
           "file": scan_file(year)}
    seen = {}
    for pno, page in enumerate(doc, start=1):
        text = page.get_text()
        res["text"].append(text)
        if not re.search(r"(?i)pertussis|indigenous|rubeola|measles", text):
            continue
        if len(re.findall(r"\d", text)) < 250:
            continue
        slope, lines = deskewed_lines(page)
        us_idx = None
        for li, line in enumerate(lines):
            if len(line) >= 4 and _key(line[0][4] + line[1][4]) == "unitedstates" and \
                    sum(1 for w in line[2:] if re.search(r"\d", w[4])) >= (len(line) - 2) * 0.7:
                us_idx = li
                break
        if us_idx is None:
            continue
        us_vals = merge_close(lines[us_idx][2:])
        us_vals = [w for w in us_vals if re.search(r"\d", w[4])]
        ncol = len(us_vals)
        anchors = [w[2] for w in us_vals]
        centers = [(w[0] + w[2]) / 2 for w in us_vals]
        if ncol < 2 or min(b - a for a, b in zip(anchors, anchors[1:])) < 14:
            continue
        # column spans: (previous right edge + 4, own right edge + 4]
        upper = [a + 4 for a in anchors]
        lower = [us_vals[0][0] - 8] + upper[:-1]

        def split(line):
            lab, cols = [], defaultdict(list)
            for w in line:
                c = (w[0] + w[2]) / 2
                if c < lower[0]:
                    lab.append(w[4])
                    continue
                for j in range(ncol):
                    if lower[j] < c <= upper[j]:
                        cols[j].append(w)
                        break
            return " ".join(lab), cols

        rows = []
        for line in lines[us_idx:]:
            lab, cols = split(line)
            area = scan_area(lab)
            if area:
                rows.append((area, lab, cols))
        if len(rows) < 45:
            continue
        us_y = (lines[us_idx][0][1] + lines[us_idx][0][3]) / 2 - slope * lines[us_idx][0][0]
        hdr = []
        for line in lines:
            ly = (line[0][1] + line[0][3]) / 2 - slope * line[0][0]
            s_ = " ".join(w[4] for w in line)
            if re.search(r"(?i)reported cases|MMWR|United States[,.]|SUMMARY TABLES|continued", s_):
                continue
            if us_y - 70 < ly < us_y - 2.5:
                hdr.extend(merge_close(line, gap=2.0))     # "Im" "ported" -> "Imported"
        texts = [[] for _ in range(ncol)]
        for w in sorted(hdr, key=lambda w: (round(w[1]), w[0])):
            if w[4] == "Area":
                continue
            c = (w[0] + w[2]) / 2
            j = min(range(ncol), key=lambda j: abs(c - centers[j]))
            texts[j].append(w[4])
        texts = [" ".join(t) for t in texts]
        try:
            cmap = classify_columns(texts, False)
        except ValueError as e:
            res["warn"].append("p%d: %s" % (pno, e))
            continue
        cmap = {d: j for d, j in cmap.items() if d in SCAN_DISEASES and d not in seen}
        if not cmap:
            continue
        for (area, lab, cols) in rows:
            for d, j in cmap.items():
                raw = "".join(w[4] for w in sorted(cols.get(j, []), key=lambda w: w[0]))
                raw = raw.replace("_", "-")
                res["cells"].append((area, lab, d, raw,
                                     "Table by geographic division and area, PDF page %d, column \"%s\""
                                     % (pno, texts[j])))
        for d, j in cmap.items():
            seen[d] = pno
            res["colmap"].append((d, pno, texts[j], us_vals[j][4]))
    res["marks"] = find_mark_defs(res["text"])
    if "-" not in res["marks"]:
        # The legend ("EXPLANATION OF SYMBOLS USED IN TABLES") is there but the
        # OCR layer lost the dash printed after the dotted leader.
        for pno, text in enumerate(res["text"], start=1):
            if re.search(r"(?i)EXPLANATION OF SYMBOLS", text) and \
                    re.search(r"(?i)No reported cases\s*\.{5,}", text):
                res["marks"]["-"] = ("No reported cases (p.%d; legend line is present, the symbol "
                                     "after the dotted leader is not legible in the OCR layer)" % pno)
                break
    return res


def scan_validate(cells, marks, disease):
    """Strict acceptance test for one disease of one scanned year.
    Returns (ok, reason, {area: (cases, flag)}). Any state cell that the OCR
    layer did not read as a number or a mark fails the disease-year."""
    need = [s for s in STATES if s != "New York"] + [NY_UP, NY_CITY, US] + list(DIVISIONS)
    got = {}
    unread = []
    for (area, label, d, raw, table) in cells:
        if d != disease or area not in need:
            continue
        num, mark, sym = parse_cell(raw)
        if num is not None:
            got[area] = (num, sym)
        elif mark == "-" and dash_is_zero(marks):
            got[area] = (0, "-" + sym)
        elif mark in ("NN", "NA", "N", "U"):
            got[area] = ("", mark)
        elif area in DIVISIONS or area == US:
            return False, "total row not readable: %s = %r" % (area, raw), got
        else:
            unread.append("%s=%r" % (area, raw))
            got[area] = ("", "unread")
    if unread:
        return False, "%d state cells not readable in the OCR layer: %s" % (
            len(unread), ", ".join(unread[:8])), got
    miss = [a for a in need if a not in got]
    if miss:
        return False, "%d rows not found: %s" % (len(miss), ", ".join(miss[:6])), got
    if got[US][0] == "":
        return False, "US total not a number", got
    n = lambda a: got[a][0] if got[a][0] != "" else 0
    for div, members in DIVISIONS.items():
        if got[div][0] == "" or sum(n(m) for m in members) != got[div][0]:
            return False, "%s: states add to %d, printed %s" % (
                div, sum(n(m) for m in members), got[div][0]), got
    if sum(n(d_) for d_ in DIVISIONS) != got[US][0]:
        return False, "divisions add to %d, printed US total %d" % (
            sum(n(d_) for d_ in DIVISIONS), got[US][0]), got
    return True, "all nine division sums and the US sum equal the printed rows", got


# --------------------------------------------------------------------------
# MMWR HTML parser (used as an independent cross-check, 2007-2015)
# --------------------------------------------------------------------------
def _txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True).replace("\xa0", " ")).strip()


def parse_mmwr_html(year):
    from bs4 import BeautifulSoup
    code = MMWR_ISSUES[year]
    fname = code + "a1.htm"
    path = os.path.join(SRC, fname)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        soup = BeautifulSoup(f.read(), "lxml")
    res = {"cells": [], "colmap": [], "warn": [], "noted_zero": "", "url": mmwr_html_url(year),
           "file": fname, "marks": {}}
    seen = {}
    tno = 0
    for table in soup.find_all("table"):
        if table.find("table"):
            continue
        trs = table.find_all("tr")
        cells = [[c for c in tr.find_all(["td", "th"])] for tr in trs]
        us_idx = None
        for i, row in enumerate(cells):
            if row and _key(_txt(row[0])) == "unitedstates":
                us_idx = i
                break
        if us_idx is None or "Alabama" not in table.get_text():
            continue
        tno += 1
        # header grid with rowspan / colspan
        grid = defaultdict(dict)       # row -> col -> cell id
        info = {}
        for r in range(us_idx):
            c = 0
            for cell in cells[r]:
                while c in grid[r]:
                    c += 1
                cs = int(cell.get("colspan") or 1)
                rs = int(cell.get("rowspan") or 1)
                cid = len(info)
                info[cid] = (r, c, cs, min(rs, us_idx - r), _txt(cell))
                for rr in range(r, min(r + rs, us_idx)):
                    for cc in range(c, c + cs):
                        grid[rr][cc] = cid
                c += cs
        width = max((max(g) + 1) for g in grid.values() if g) if grid else 0
        # leaf cells: nothing printed below them
        leaves = []
        for cid, (r, c, cs, rs, t) in info.items():
            if t.upper().startswith("TABLE") or cs >= width:
                continue
            below = set()
            for rr in range(r + rs, us_idx):
                for cc in range(c, c + cs):
                    if cc in grid[rr] and grid[rr][cc] != cid:
                        below.add(grid[rr][cc])
            if not below:
                above = []
                for rr in range(0, r):
                    for cc in range(c, c + cs):
                        o = grid[rr].get(cc)
                        if o is not None and o != cid and o not in above:
                            ot = info[o][4]
                            if not ot.upper().startswith("TABLE") and info[o][2] < width:
                                above.append(o)
                leaves.append((c, r, " | ".join([info[o][4] for o in above] + [t])))
        leaves.sort()
        texts = [t for (_, _, t) in leaves if _key(t) != "area"]
        texts = [t for t in texts if t != ""]
        us_cells = [_txt(c) for c in cells[us_idx]][1:]
        if len(texts) != len(us_cells):
            if re.search(r"(?i)measles|mumps|pertussis|rubella|diphtheria|paralytic|hepatitis",
                         " ".join(texts)):
                res["warn"].append("html table %d: %d header leaves vs %d data cells: %r" %
                                   (tno, len(texts), len(us_cells), texts))
            continue
        try:
            cmap = classify_columns(texts, "hepatitis" in " ".join(texts).lower())
        except ValueError as e:
            res["warn"].append("html table %d: %s" % (tno, e))
            continue
        for d, j in cmap.items():
            if d in seen:
                continue
            seen[d] = tno
            res["colmap"].append((d, tno, texts[j], us_cells[j]))
            for row in cells[us_idx:]:
                if not row:
                    continue
                label = _txt(row[0])
                area = area_of(label)
                vals = [_txt(c) for c in row[1:]]
                if area is None:
                    continue
                if len(vals) != len(texts):
                    res["warn"].append("html table %d: row %r has %d cells" % (tno, label, len(vals)))
                    continue
                res["cells"].append((area, label, d, vals[j], "Table 2, HTML table %d, column \"%s\"" %
                                     (tno, texts[j])))
    full = _txt(soup)
    res["fulltext"] = full
    return res


# --------------------------------------------------------------------------
# NNDSS annual tables (Stacks text files)
# --------------------------------------------------------------------------
def nndss_label_to_disease(label):
    t = re.sub(r"<[^>]+>", "", label)
    t = re.sub(r"[^A-Za-z,;<> ()-]", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower().rstrip(",")
    table = {
        "measles, total": "measles", "measles, indigenous": "measles_indigenous",
        "measles, imported": "measles_imported", "measles": "measles",
        "mumps": "mumps", "pertussis": "pertussis", "rubella": "rubella",
        "diphtheria": "diphtheria", "poliomyelitis, paralytic": "polio_paralytic",
    }
    if t in table:
        return table[t]
    # "Hepatitis, A, acute" (2016-2019), "Hepatitis, Viral Disease, Hepatitis A" (2020-2022)
    if re.search(r"hepatitis,? a\b", t) and not re.search(r"\b[bc]\b|confirmed|probable|perinatal", t):
        return "hepatitis_a"
    if "hepatitis" in t and re.search(r"\ba\b", t):
        return "hepatitis_a?" + t          # reported as a problem, not used
    return None


def parse_nndss_txt(path):
    with open(path, "rb") as f:
        raw = f.read().decode("cp1252", errors="replace")
    lines = raw.replace("\r", "").split("\n")
    title = re.sub(r"<[^>]+>", "", lines[0]).strip()
    m = re.match(r"(?i)table\s*(2[a-z])\.", title)
    ym = re.search(r"(20\d\d)", title)
    if not m or not ym:
        return None
    table, year = "Table " + m.group(1).lower(), int(ym.group(1))
    try:
        i0 = next(i for i, l in enumerate(lines) if l.lower().startswith("column labels"))
        i1 = next(i for i, l in enumerate(lines) if l.lower().startswith("tab delimited data"))
    except StopIteration:
        return None
    labels = [l.strip() for l in lines[i0 + 1:i1] if l.strip()]
    if labels and _key(labels[0]) in ("reportingarea", "area"):
        labels = labels[1:]
    out = {"year": year, "table": table, "title": title, "labels": labels, "rows": [],
           "marks": {}, "warn": [], "tail": []}
    data_done = False
    for l in lines[i1 + 1:]:
        if not data_done:
            if not l.strip():
                if out["rows"]:
                    data_done = True
                continue
            parts = l.split("\t")
            if len(parts) != len(labels) + 1:
                out["warn"].append("%s %d: row %r has %d fields, expected %d" %
                                   (table, year, parts[0], len(parts) - 1, len(labels)))
                continue
            out["rows"].append((parts[0].strip(), [p.strip() for p in parts[1:]]))
        else:
            out["tail"].append(l)
            m2 = MARK_DEF_RE.match(l)
            if m2:
                mk = "-" if m2.group(1)[0] in DASHES else m2.group(1)
                out["marks"].setdefault(mk, m2.group(2).strip())
    return out


def parse_nndss_pdf(path):
    """2023 annual tables (PDF only on Stacks). Labels can wrap over two or
    three lines with the numbers set at the middle height, and the table
    continues on a second page with the header repeated and no US row."""
    import fitz
    doc = fitz.open(path)
    first = doc[0].get_text()
    m = re.search(r"Table\s*(2[a-z])\.", first)
    ym = re.search(r"Residents, (20\d\d)", re.sub(r"\s+", " ", first))
    if not m or not ym:
        return None
    out = {"year": int(ym.group(1)), "table": "Table " + m.group(1), "labels": [], "rows": [],
           "marks": {}, "warn": [], "tail": [], "title": ""}
    ncol = None
    alltext = []
    for pno, page in enumerate(doc, start=1):
        alltext.append(page.get_text())
        lines = pdf_lines(page)
        items = []
        for line in lines:
            y = (line[0][1] + line[0][3]) / 2
            label, vals = split_row(line)
            items.append([y, label, vals, line])
        valued = [it for it in items if it[2]]
        if not valued:
            continue
        edges = [t[1] for v in valued for t in v[2] if area_of(v[1]) or not v[1]]
        if not edges:
            continue
        label_edge = min(edges)
        # glue label-only fragments to the value line they wrap around; a
        # fragment has to sit in the label column (header words do not)
        for it in items:
            if it[2] or not it[1]:
                continue
            if max(w[2] for w in it[3]) >= label_edge:
                continue
            near = [v for v in valued if abs(v[0] - it[0]) < 9.5]
            if len(near) == 1:
                v = near[0]
                v[1] = (it[1] + " " + v[1]).strip() if it[0] < v[0] else (v[1] + " " + it[1]).strip()
                it[1] = ""
        us = [v for v in valued if area_of(v[1]) == US]
        if us and ncol is None:
            us = us[0]
            ncol = len(us[2])
            centers = [(t[1] + t[2]) / 2 for t in us[2]]
            texts = [[] for _ in range(ncol)]
            hdr = []
            for it in items:
                s_ = " ".join(w[4] for w in it[3])
                if it[0] < us[0] - 2.5 and it[0] > us[0] - 70 and not it[2] \
                        and not re.search(r"Table 2|Nationally Notifiable|Residents", s_):
                    hdr.extend(it[3])
            hdr.sort(key=lambda w: (round(w[1]), w[0]))
            for w in hdr:
                if w[4] in ("Reporting", "Area"):
                    continue
                c = (w[0] + w[2]) / 2
                j = min(range(ncol), key=lambda j: abs(c - centers[j]))
                texts[j].append(w[4].replace("\u200b", ""))
            out["labels"] = [" ".join(t) for t in texts]
        if ncol is None:
            continue
        for v in valued:
            area = area_of(v[1])
            if area is None:
                continue
            if len(v[2]) != ncol:
                out["warn"].append("%s p%d: row %r has %d values, expected %d" %
                                   (out["table"], pno, v[1], len(v[2]), ncol))
                continue
            if any(r[0] == v[1] for r in out["rows"]):
                continue
            out["rows"].append((v[1], [t[0] for t in v[2]]))
    out["marks"] = find_mark_defs(alltext)
    out["tail"] = "\n".join(alltext).splitlines()
    return out


# --------------------------------------------------------------------------
# Assemble
# --------------------------------------------------------------------------
def dash_is_zero(marks):
    d = marks.get("-", "")
    return bool(re.search(r"(?i)no reported cases", d))


def cell_to_record(raw, marks):
    """-> (cases or '', flag)"""
    num, mark, sym = parse_cell(raw)
    if num is not None:
        return num, sym
    if mark == "-" and dash_is_zero(marks):
        return 0, "-" + sym
    return "", mark + sym


def combine_ny(up, city):
    """up/city: (cases, flag). New York = upstate + New York City."""
    (c1, f1), (c2, f2) = up, city
    if c1 != "" and c2 != "":
        flag = "sum" if (f1.startswith("sum") or f2.startswith("sum")) else ""
        r1, r2 = f1.replace("sum", ""), f2.replace("sum", "")
        if r1.startswith("-") and r2.startswith("-"):
            flag += "-"
        flag += "".join(sorted(set((r1 + r2).replace("-", ""))))
        return c1 + c2, flag
    parts = []
    if c1 == "":
        parts.append("upstate:" + f1)
    if c2 == "":
        parts.append("NYC:" + f2)
    known = [c for c in (c1, c2) if c != ""]
    # one part is not a number: no New York total is printed, so leave cases
    # blank and say which part is missing and what the other part was
    note = ";".join(parts)
    if known:
        note += ";other part=%d" % known[0]
    return "", note


def no_cases_statement(text, year):
    """Diseases the issue says had no US cases that year, so that Table 2
    carries no column for them. Returns {disease: sentence as printed}."""
    out = {}
    text = re.sub(r"\s+", " ", text)
    pats = [
        r"No cases of ((?:(?!No cases of).){5,1500}?) (?:were|was) reported "
        r"(?:in the United States )?(?:in|during) (\d{4})",
        r"There were no reported cases of ((?:(?!no reported cases).){5,400}?) "
        r"in the United States during (\d{4})",
    ]
    for pat in pats:
        for m in re.finditer(pat, text):
            if int(m.group(2)) != year:
                continue
            lst = m.group(1).lower()
            sentence = m.group(0)
            if "diphtheria" in lst:
                out.setdefault("diphtheria", sentence)
            if re.search(r"poliomyelitis,? paralytic|paralytic poliomyelitis", lst):
                out.setdefault("polio_paralytic", sentence)
            if re.search(r"rubella(?!,? congenital)", lst):
                out.setdefault("rubella", sentence)
            if "measles" in lst:
                out.setdefault("measles", sentence)
    return out


def finality_statement(text):
    text = re.sub(r"\s+", " ", text).replace("\xad ", "").replace("other- wise", "otherwise")
    m = re.search(r"[^.]*final totals[^.]{0,80}as of [A-Z][a-z]+ \d{1,2}, \d{4}[^.]*\.", text)
    if not m:
        m = re.search(r"[^.]*compiled in final form[^.]*\.", text)
    return m.group(0).strip() if m else ""


def nndss_finality(tail_text):
    t = re.sub(r"\s+", " ", tail_text)
    found = []
    for pat in [r"\d{4} data are reported through [A-Z][a-z]+ \d{1,2}, \d{4}",
                r"NNDSS data displayed in the annual tables are accurate as of [A-Z][a-z]+ \d{1,2}, \d{4}",
                r"[^.]*\bfinal(?:ized)? \d{4} data[^.]*",
                r"[^.]*\bdata (?:are|were) (?:final|finalized)[^.]*",
                r"[^.]*as of [A-Z][a-z]+ \d{1,2}, \d{4}[^.]*"]:
        for m in re.finditer(pat, t):
            x = m.group(0).strip()
            if x not in found and not any(x in f for f in found) and "opulation" not in x:
                found.append(x)
    return " // ".join(found)[:900]


def main():
    if "--no-download" not in sys.argv:
        download_all()
    out_rows, area_rows, sumcheck, markrows, colrows, htmlcmp, problems = [], [], [], [], [], [], []
    finalrows = []
    scanrows = []

    def emit(year, cells, marks, url, fname, zero_note=None):
        """cells: list of (area, label, disease, raw, table)."""
        by = defaultdict(dict)
        tab = {}
        for (area, label, d, raw, table) in cells:
            cases, flag = cell_to_record(raw, marks)
            by[d][area] = (cases, flag)
            tab[d] = table
            area_rows.append([year, area, label, d, cases, flag, raw, url, fname, table])
        emit_by(year, by, tab, url, fname, zero_note)
        for k, v in sorted(marks.items()):
            markrows.append([year, fname, k, v])

    def emit_by(year, by, tab, url, fname, zero_note=None):
        # measles total where the table prints only indigenous and imported
        if "measles" not in by and "measles_indigenous" in by and "measles_imported" in by:
            by["measles"] = {}
            for area in by["measles_indigenous"]:
                a = by["measles_indigenous"][area]
                b = by["measles_imported"].get(area)
                if b is None:
                    continue
                if a[0] != "" and b[0] != "":
                    f = "sum" if not (a[1].startswith("-") and b[1].startswith("-")) else "sum-"
                    by["measles"][area] = (a[0] + b[0], f)
                else:
                    by["measles"][area] = ("", "sum:" + a[1] + "/" + b[1])
            tab["measles"] = re.sub(r', column ".*$', "", tab["measles_indigenous"]) + \
                ", computed as indigenous + imported (no total column printed)"
        for d in DISEASES:
            if d not in by:
                continue
            got = by[d]
            total, missing, marks_seen = 0, [], []
            for st in STATES:
                if st == "New York":
                    if "New York" in got:
                        rec = got["New York"]
                    elif NY_UP in got and NY_CITY in got:
                        rec = combine_ny(got[NY_UP], got[NY_CITY])
                    else:
                        missing.append(st)
                        continue
                elif st in got:
                    rec = got[st]
                else:
                    missing.append(st)
                    continue
                out_rows.append([year, st, d, rec[0], rec[1], url, fname, tab[d]])
                if rec[0] != "":
                    total += rec[0]
                else:
                    marks_seen.append("%s=%s" % (st, rec[1]))
            usrec = got.get(US, ("", "missing"))
            ok = (usrec[0] != "" and usrec[0] == total and not missing)
            sumcheck.append([year, d, total, usrec[0], usrec[1],
                             "" if usrec[0] == "" else usrec[0] - total,
                             "OK" if ok else "CHECK", ";".join(missing), ";".join(marks_seen), fname])
        if zero_note:
            for d, sentence in zero_note.items():
                if d in by:
                    continue
                for st in STATES:
                    out_rows.append([year, st, d, 0, "fn0", url, fname,
                                     'Table 2 footnote: "%s"' % sentence[:300]])
                sumcheck.append([year, d, 0, 0, "fn0", 0, "OK (footnote: no cases in US)", "", "", fname])

    # ---- 1980-1992 scanned annual summaries (measles and pertussis only)
    for year in sorted(SCAN_ISSUES):
        sc = parse_scan_pdf(year)
        if sc is None:
            problems.append("%d: scan not downloaded" % year)
            scanrows.append([year, "", "no", "file not downloaded", "", "", ""])
            continue
        heads = {d: (pno, text, usval) for (d, pno, text, usval) in sc["colmap"]}
        results = {}
        for d in ("measles", "measles_indigenous", "measles_imported", "pertussis"):
            if d not in heads:
                continue
            results[d] = scan_validate(sc["cells"], sc["marks"], d)
        split = "measles_indigenous" in heads or "measles_imported" in heads
        accept = set()
        if "pertussis" in results and results["pertussis"][0]:
            accept.add("pertussis")
        if split:
            if all(d in results and results[d][0] for d in ("measles_indigenous", "measles_imported")):
                accept.update(["measles_indigenous", "measles_imported"])
        elif "measles" in results and results["measles"][0]:
            accept.add("measles")
        for d in ("measles", "measles_indigenous", "measles_imported", "pertussis"):
            if d in results:
                why = results[d][1]
                if results[d][0] and d not in accept:
                    why += "; not used because the other measles column failed"
                scanrows.append([year, d, "yes" if d in accept else "no", why,
                                 heads[d][0], heads[d][1], heads[d][2], sc["file"]])
            elif d != "measles" or not split:
                if not (d.startswith("measles_") and "measles" in heads):
                    scanrows.append([year, d, "no", "column not found in the OCR text layer", "", "", "",
                                     sc["file"]])
        finalrows.append([year, sc["file"], finality_statement(" ".join(sc["text"]))])
        if not accept:
            continue
        by, tab = defaultdict(dict), {}
        for (area, label, d, raw, table) in sc["cells"]:
            if d in accept and area in results[d][2]:
                by[d][area] = results[d][2][area]
                tab[d] = table + " (scan, OCR text layer)"
                area_rows.append([year, area, label, d, by[d][area][0], by[d][area][1], raw,
                                  sc["url"], sc["file"], tab[d]])
        for (d, pno, text, usval) in sc["colmap"]:
            if d in accept:
                colrows.append([year, "scan pdf", d, pno, text, usval])
        emit_by(year, by, tab, sc["url"], sc["file"])
        for k, v in sorted(sc["marks"].items()):
            markrows.append([year, sc["file"], k, v])

    # ---- 1993-2015 MMWR summaries
    for year in sorted(MMWR_ISSUES):
        pdf = parse_mmwr_pdf(year)
        if pdf is None:
            problems.append("%d: PDF missing" % year)
            continue
        for w in pdf["warn"]:
            problems.append("%d pdf %s" % (year, w))
        for (d, pno, text, usval) in pdf["colmap"]:
            colrows.append([year, "pdf", d, pno, text, usval])
        fulltext = " ".join(pdf["text"])
        zero = no_cases_statement(fulltext, year)
        finalrows.append([year, pdf["file"], finality_statement(fulltext)])
        emit(year, pdf["cells"], pdf["marks"], pdf["url"], pdf["file"], zero)
        if year in HTML_YEARS:
            html = parse_mmwr_html(year)
            if html is None:
                problems.append("%d: HTML missing" % year)
                continue
            for w in html["warn"]:
                problems.append("%d %s" % (year, w))
            for (d, tno, text, usval) in html["colmap"]:
                colrows.append([year, "html", d, tno, text, usval])
            p = {(a, d): raw for (a, _, d, raw, _) in pdf["cells"]}
            h = {(a, d): raw for (a, _, d, raw, _) in html["cells"]}
            for d in DISEASES:
                pk = {k for k in p if k[1] == d}
                hk = {k for k in h if k[1] == d}
                if not pk and not hk:
                    continue
                diff = []
                for k in sorted(pk | hk):
                    a = parse_cell(p[k])[:2] if k in p else ("absent", "")
                    b = parse_cell(h[k])[:2] if k in h else ("absent", "")
                    if k[0] == "Territories":
                        continue
                    if a != b:
                        diff.append("%s: pdf=%s html=%s" % (k[0], p.get(k, "absent"), h.get(k, "absent")))
                htmlcmp.append([year, d, len(pk), len(hk), len(diff), " ; ".join(diff)])

    # ---- 2016-2023 NNDSS annual tables
    for year in sorted(NNDSS_SOURCES):
        got_any = set()
        final_done = False
        for spec in NNDSS_SOURCES[year]:
            kind, url, fname = nndss_local(spec)
            if fname is None:
                problems.append("%d: NNDSS source %r not downloaded" % (year, spec))
                continue
            path = os.path.join(SRC, fname)
            t = parse_nndss_pdf(path) if kind == "stacks_pdf" else parse_nndss_txt(path)
            if t is None:
                problems.append("%d: %s not parseable" % (year, fname))
                continue
            if t["year"] != year:
                problems.append("%s says year %d, expected %d" % (fname, t["year"], year))
                continue
            for w in t["warn"]:
                problems.append("%d %s" % (year, w))
            if not final_done:
                finalrows.append([year, fname, nndss_finality("\n".join(t["tail"]))])
                final_done = True
            if kind == "stacks_pdf":
                try:
                    dmap = classify_columns(t["labels"], "hepatitis" in " ".join(t["labels"]).lower())
                except ValueError as e:
                    problems.append("%d %s: %s" % (year, fname, e))
                    continue
            else:
                dmap = {}
                for j, lab in enumerate(t["labels"]):
                    d = nndss_label_to_disease(lab)
                    if d is None:
                        continue
                    if d.startswith("hepatitis_a?"):
                        problems.append("%d %s: hepatitis A column not used: %r" % (year, t["table"], lab))
                        continue
                    dmap[d] = j
            us = [r for r in t["rows"] if area_of(r[0]) == US]
            for d, j in dmap.items():
                clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t["labels"][j])).strip()
                clean = clean.replace("\ufffd", "").strip()
                colrows.append([year, "nndss " + kind, d, t["table"], clean, us[0][1][j] if us else ""])
                tcells = []
                for (label, vals) in t["rows"]:
                    area = area_of(label)
                    if area is None:
                        problems.append("%d %s: unknown area %r" % (year, t["table"], label))
                        continue
                    tcells.append((area, label, d, vals[j], '%s, column "%s"' % (t["table"], clean)))
                emit(year, tcells, t["marks"], url, fname)
                got_any.add(d)
        miss = [d for d in DISEASES if d not in got_any]
        if miss:
            problems.append("%d: not found in NNDSS tables: %s" % (year, ", ".join(miss)))

    # ---- write
    def write(name, header, rows):
        with open(os.path.join(BRIDGE, name), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    out_rows.sort(key=lambda r: (r[0], DISEASES.index(r[2]), r[1]))
    write("annual_state_cases.csv",
          ["year", "state", "disease", "cases", "flag", "source_url", "source_file", "source_table"],
          out_rows)
    write("annual_area_cases_all.csv",
          ["year", "area", "area_as_printed", "disease", "cases", "flag", "cell_as_printed",
           "source_url", "source_file", "source_table"], area_rows)
    write("checks_state_sum_vs_us.csv",
          ["year", "disease", "sum_of_states", "us_total_row", "us_flag", "us_minus_states",
           "result", "states_missing", "states_with_non_numeric_mark", "source_file"], sumcheck)
    write("checks_html_vs_pdf.csv",
          ["year", "disease", "pdf_cells", "html_cells", "cells_differing", "differences"], htmlcmp)
    write("checks_marks.csv", ["year", "source_file", "mark", "definition_as_printed"],
          sorted(set(map(tuple, markrows))))
    write("checks_scans_1980_1992.csv",
          ["year", "disease", "used", "result_of_strict_check", "pdf_page", "column_header_as_read",
           "us_total_as_read", "source_file"], scanrows)
    write("checks_finality.csv", ["year", "source_file", "statement_as_printed"], finalrows)
    write("checks_column_map.csv",
          ["year", "source", "disease", "page_or_table", "printed_column_header", "us_total_cell"],
          colrows)

    # ---- OWID cross-check (measles only; never used as a source)
    owid_path = os.path.join(SRC, "owid_measles_states_crosscheck_only.csv")
    owid_rows = []
    if os.path.exists(owid_path):
        mine = {(r[0], r[1]): r[3] for r in out_rows if r[2] == "measles"}
        with open(owid_path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                st = r.get("country") or r.get("state") or r.get("entity")
                try:
                    y = int(r["year"])
                    oc = int(float(r["cases"]))
                except (KeyError, ValueError, TypeError):
                    continue
                if (y, st) in mine:
                    mc = mine[(y, st)]
                    owid_rows.append([y, st, mc, oc, "same" if mc == oc else "DIFFERENT",
                                      r.get("source", "")])
    write("checks_owid_measles.csv", ["year", "state", "this_file", "owid", "result", "owid_source"],
          sorted(owid_rows))

    # ---- console summary
    print("\nrows written: %d" % len(out_rows))
    cov = defaultdict(set)
    for r in out_rows:
        cov[r[2]].add(r[0])
    years = sorted({r[0] for r in out_rows})
    print("\ncoverage (x = 51 areas present):")
    print("%-20s %s" % ("", " ".join(str(y)[2:] for y in years)))
    for d in DISEASES:
        print("%-20s %s" % (d, " ".join(" x" if y in cov[d] else " ." for y in years)))
    bad = [s for s in sumcheck if not s[6].startswith("OK")]
    print("\nstate sum vs US total: %d disease-years checked, %d not equal" % (len(sumcheck), len(bad)))
    for s in bad:
        print("  ", s[:8], s[8][:160])
    nd = [h for h in htmlcmp if h[4]]
    print("\nHTML vs PDF: %d disease-years compared, %d with differences" % (len(htmlcmp), len(nd)))
    for h in nd:
        print("  ", h[0], h[1], h[4], h[5][:300])
    diff = [o for o in owid_rows if o[4] != "same"]
    print("\nOWID measles: %d state-years compared, %d different" % (len(owid_rows), len(diff)))
    for o in diff:
        print("  ", o[:4])
    if problems:
        print("\nproblems / warnings:")
        for p in problems:
            print("  ", p)


if __name__ == "__main__":
    main()
