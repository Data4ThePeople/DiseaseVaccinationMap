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
        if "pertussis" in t or "whooping" in t:     # "Whooping cough" in the 1950s
            put("pertussis", i)
        if "diphtheria" in t:
            put("diphtheria", i)
        if "rubella" in t and "cong" not in t and "syndrome" not in t:
            put("rubella", i)
        # "Non- paralytic" and "Non\xadparalytic" (line-broken headers in the 1950s scans) are not paralytic
        if "paralytic" in t and not re.search(r"non[\xad\s-]*paralytic", t):
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
            if "measles" in t and "german" not in t and "rubella" not in t:     # "Rubella (German measles)"
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
# Measles, pertussis and mumps are read from these. A disease-year is used
# only if every state cell reads as a number or a defined mark, the states of
# every geographic division add up to the printed division row, the divisions
# add up to the printed United States row, and the states add up to the
# printed United States row. Cells the OCR layer damaged may be read from the
# rendered page image (SCAN_IMAGE_CELLS below); nothing is filled in to make
# a sum work.
SCAN_ISSUES = {
    1992: 36063, 1991: 36010, 1990: 35905, 1989: 35853, 1988: 35958, 1987: 35629,
    1986: 35496, 1985: 35429, 1984: 35267, 1983: 35188, 1982: 35066, 1981: 1307,
    1980: 1484,
    # 1968-1979: read for mumps only. 1977 and 1978 sit in the Stacks MMWR
    # collection (cdc:101) rather than the NNDSS collection.
    1979: 1577, 1978: 10895, 1977: 10894, 1976: 1130, 1975: 1041, 1974: 1743,
    1973: 1849, 1972: 1895, 1971: 1829, 1970: 951, 1969: 838, 1968: 1717,
    # 1956-1967: read for pertussis and measles; 1966 and 1967
    # also for hepatitis A (the column is "Hepatitis, infectious" until 1972). 1956 (10893) is in the MMWR
    # collection; the others are in the NNDSS collection.
    1967: 1555, 1966: 615, 1965: 740, 1964: 698, 1963: 491, 1962: 380, 1961: 1427,
    1960: 1360, 1959: 1302, 1958: 1162, 1957: 1035, 1956: 10893,
}
SCAN_DISEASES = ("measles", "measles_indigenous", "measles_imported", "pertussis", "mumps",
                 "hepatitis_a", "polio_paralytic")

# Misprinted cells whose reading is an editor's decision rather than a plain read
# of the page. Their flag says so.
SCAN_EDITOR_READINGS = {
    (1971, "mumps", "District of Columbia"): 'printed "-99", read as 99 by editor decision 2026-10-06',
    (1971, "mumps", "Ohio"): 'printed "8.784", read as 8,784 by editor decision 2026-10-06',
    (1963, "measles", "Hawaii"): 'printed "3.623", read as 3,623 by editor decision 2026-10-10',
}

# Cells read by eye from a rendered page image (PyMuPDF, 400 dpi crop of the
# table) where the OCR text layer is damaged. Key: (year, disease, area as in
# AREA_KEYS); value: (text as printed on the image, PDF page). Every entry is
# listed in checks_image_cells.csv with what the OCR layer had. A year is
# still kept only if the strict sum test passes exactly afterwards.
SCAN_IMAGE_CELLS = {
    # 1971 mumps, PDF page 10. Two cells are misprinted on the page; Eric accepted
    # the readings below on October 6, 2026 (see SCAN_EDITOR_READINGS).
    (1971, "mumps", "Illinois"): ("5,585", 10),
    (1971, "mumps", "New Jersey"): ("1,819", 10),
    (1971, "mumps", "Virginia"): ("1,073", 10),
    (1971, "mumps", "Georgia"): ("-", 10),
    (1971, "mumps", "East South Central"): ("8,933", 10),
    (1971, "mumps", "Arkansas"): ("157", 10),
    (1971, "mumps", "Oregon"): ("1,772", 10),
    (1971, "mumps", "District of Columbia"): ("99", 10),   # printed "-99"
    (1971, "mumps", "Ohio"): ("8,784", 10),                # printed "8.784"
    # 1989 mumps, PDF page 13: dashes the OCR layer did not pick up
    (1989, "mumps", "Maine"): ("-", 13),
    (1989, "mumps", "Rhode Island"): ("-", 13),
    (1989, "mumps", "North Dakota"): ("-", 13),
    (1989, "mumps", "South Dakota"): ("-", 13),
    # 1984 mumps, PDF page 16: OCR read the comma as a period
    (1984, "mumps", "East North Central"): ("1,172", 16),
    # 1982 mumps, PDF page 16
    (1982, "mumps", "Vermont"): ("7", 16),
    (1982, "mumps", "Pennsylvania"): ("160", 16),
    (1982, "mumps", "Ohio"): ("1,775", 16),
    (1982, "mumps", "North Dakota"): ("-", 16),
    (1982, "mumps", "South Atlantic"): ("286", 16),
    (1982, "mumps", "District of Columbia"): ("-", 16),
    (1982, "mumps", "Georgia"): ("30", 16),
    (1982, "mumps", "East South Central"): ("68", 16),
    (1982, "mumps", "Mississippi"): ("11", 16),
    # 1983 mumps, PDF page 21
    (1983, "mumps", "Maine"): ("30", 21),
    (1983, "mumps", "New Hampshire"): ("29", 21),
    (1983, "mumps", "Rhode Island"): ("16", 21),
    (1983, "mumps", "Minnesota"): ("30", 21),
    (1983, "mumps", "North Dakota"): ("3", 21),
    (1983, "mumps", "South Dakota"): ("-", 21),
    (1983, "mumps", "Delaware"): ("10", 21),
    (1983, "mumps", "South Carolina"): ("14", 21),
    (1983, "mumps", "Georgia"): ("63", 21),
    (1983, "mumps", "Tennessee"): ("30", 21),
    (1983, "mumps", "Alabama"): ("2", 21),
    (1983, "mumps", "Arkansas"): ("3", 21),
    (1983, "mumps", "Montana"): ("9", 21),
    (1983, "mumps", "Idaho"): ("9", 21),
    (1983, "mumps", "Wyoming"): ("3", 21),
    (1983, "mumps", "Colorado"): ("54", 21),
    (1983, "mumps", "New Mexico"): ("NN", 21),
    # 1986 mumps, PDF page 12 (the Alaska, Mississippi and upstate New York
    # labels are missing from the OCR layer altogether)
    (1986, "mumps", "Maine"): ("-", 12),
    (1986, "mumps", NY_UP): ("79", 12),
    (1986, "mumps", "Tennessee"): ("1,476", 12),
    (1986, "mumps", "Mississippi"): ("NN", 12),
    (1986, "mumps", "Wyoming"): ("-", 12),
    (1986, "mumps", "Colorado"): ("17", 12),
    (1986, "mumps", "Utah"): ("16", 12),
    (1986, "mumps", "Nevada"): ("11", 12),
    (1986, "mumps", "Pacific"): ("416", 12),
    (1986, "mumps", "Washington"): ("30", 12),
    (1986, "mumps", "Oregon"): ("NN", 12),
    (1986, "mumps", "California"): ("354", 12),
    (1986, "mumps", "Alaska"): ("8", 12),
    (1986, "mumps", "Hawaii"): ("24", 12),
    # 1968 mumps, PDF page 10 (Table: reported cases by division and state)
    (1968, "mumps", "Alaska"): ("705", 10),
    # 1970 mumps, PDF page 10 (Table 6)
    (1970, "mumps", "Oklahoma"): ("2,683", 10),
    # 1972 mumps, PDF page 10
    (1972, "mumps", "East South Central"): ("3,859", 10),
    # 1979 mumps, PDF page 13 (division labels and several state labels are
    # missing from the OCR layer)
    (1979, "mumps", "New England"): ("768", 13),
    (1979, "mumps", "Middle Atlantic"): ("1,360", 13),
    (1979, "mumps", "East North Central"): ("6,056", 13),
    (1979, "mumps", "Indiana"): ("360", 13),
    (1979, "mumps", "West North Central"): ("760", 13),
    (1979, "mumps", "South Atlantic"): ("883", 13),
    (1979, "mumps", "District of Columbia"): ("2", 13),
    (1979, "mumps", "Virginia"): ("105", 13),
    (1979, "mumps", "South Carolina"): ("5", 13),
    (1979, "mumps", "East South Central"): ("1,623", 13),
    (1979, "mumps", "Kentucky"): ("1,378", 13),
    (1979, "mumps", "Tennessee"): ("108", 13),
    (1979, "mumps", "West South Central"): ("1,429", 13),
    (1979, "mumps", "Arkansas"): ("489", 13),
    (1979, "mumps", "Mountain"): ("334", 13),
    (1979, "mumps", "New Mexico"): ("15", 13),
    (1979, "mumps", "Arizona"): ("66", 13),
    (1979, "mumps", "Pacific"): ("1,012", 13),
    (1979, "mumps", "Oregon"): ("118", 13),
    # 1980 mumps, PDF page 19 (the OCR layer lost or garbled these row labels)
    (1980, "mumps", "New England"): ("618", 19),
    (1980, "mumps", "Middle Atlantic"): ("970", 19),
    (1980, "mumps", NY_UP): ("174", 19),
    (1980, "mumps", "East North Central"): ("3,311", 19),
    (1980, "mumps", "North Dakota"): ("4", 19),
    (1980, "mumps", "South Dakota"): ("3", 19),
    # 1981 mumps, PDF page 79 ("MUMPS - Reported cases, by area and age",
    # Total column; the OCR layer read Louisiana's 6 as 76)
    (1981, "mumps", "New Hampshire"): ("26", 79),
    (1981, "mumps", "Vermont"): ("10", 79),
    (1981, "mumps", NY_CITY): ("95", 79),
    (1981, "mumps", "Ohio"): ("687", 79),
    (1981, "mumps", "Illinois"): ("343", 79),
    (1981, "mumps", "Iowa"): ("94", 79),
    (1981, "mumps", "North Dakota"): ("-", 79),
    (1981, "mumps", "South Atlantic"): ("601", 79),
    (1981, "mumps", "Delaware"): ("10", 79),
    (1981, "mumps", "West Virginia"): ("120", 79),
    (1981, "mumps", "Arkansas"): ("7", 79),
    (1981, "mumps", "Louisiana"): ("6", 79),
    (1981, "mumps", "Oklahoma"): ("NN", 79),
    (1981, "mumps", "Idaho"): ("8", 79),
    (1981, "mumps", "New Mexico"): ("NN", 79),
    # 1987 mumps, PDF page 12
    (1987, "mumps", "Massachusetts"): ("21", 12),
    (1987, "mumps", "Rhode Island"): ("-", 12),
    (1987, "mumps", "Connecticut"): ("16", 12),
    (1987, "mumps", "Middle Atlantic"): ("342", 12),
    (1987, "mumps", "Pennsylvania"): ("86", 12),
    (1987, "mumps", "Minnesota"): ("810", 12),
    (1987, "mumps", "Montana"): ("9", 12),
    (1987, "mumps", "Idaho"): ("7", 12),
    (1987, "mumps", "Colorado"): ("34", 12),
    (1987, "mumps", "New Mexico"): ("NN", 12),
    (1987, "mumps", "Utah"): ("12", 12),
    (1987, "mumps", "Nevada"): ("5", 12),
    (1987, "mumps", "Pacific"): ("490", 12),
    (1987, "mumps", "Washington"): ("70", 12),
    (1987, "mumps", "California"): ("397", 12),
}
# Table pages where the OCR layer lost a column header or a US total entirely.
# "insert_us": (x0, x1, text) of a US-row cell read from the page image, placed
# at the column's position on the page; "headers": column index (left to right,
# after the insert) -> header text read from the page image.
SCAN_PAGE_FIXES = {
    # 1981: measles is in its own table, "MEASLES (Rubeola) - Reported cases, by
    # area and month"; its first column is "Total".
    (1981, 70): {"headers": {0: "Measles (Rubeola) Total"}, "only_these_headers": True,
                 "min_rows": 5},
    # 1960 Table 5, p.9: numbers and row labels sit at different heights and the
    # OCR layer splits every row; the pertussis column is read from the image.
    (1960, 9): {"image_only": {"pertussis": ("PERTUSSIS (whooping cough)", "14,809"),
                               "measles": ("MEASLES", "441,703")}},
    (1986, 12): {"insert_us": [(124.0, 137.0, "327*")],
                 "headers": {0: "Measles Indigenous", 1: "Measles Imported"}},
    # Hepatitis A. 1967 Table 6, p.9 and 1977 Table 5, p.11: the OCR layer has no
    # usable United States row (1977 is also skewed by most of a row), so the
    # whole column is read from the image.
    (1967, 9): {"image_only": {"hepatitis_a": ("HEPATITIS INFECTIOUS", "38,909")}},
    (1977, 11): {"image_only": {"hepatitis_a": ("VIRAL HEPATITIS A", "31,153")}},
    (1986, 11): {"headers": {0: "Hepatitis A"}},
    (1991, 20): {"headers": {0: "Hepatitis A"}},
}

# Measles and pertussis cells read from the page image (same rules as above).
_MP_IMAGE = """
# year | disease | area | text on the image | PDF page
1989 | measles_indigenous | Maine | - | 13
1989 | measles_indigenous | South Dakota | - | 13
1989 | measles_indigenous | Idaho | - | 13
1989 | measles_indigenous | Wyoming | - | 13
1989 | measles_imported | Oklahoma | - | 13
1989 | measles_imported | Wyoming | - | 13
1989 | pertussis | Wyoming | - | 13
1988 | pertussis | Nevada | 2 | 15
1988 | pertussis | Oregon | 53 | 15
1988 | pertussis | California | 270 | 15
1988 | pertussis | Hawaii | 50 | 15
1987 | measles_indigenous | Minnesota | 19 | 12
1987 | measles_indigenous | South Dakota | - | 12
1987 | measles_indigenous | Nebraska | - | 12
1987 | measles_indigenous | Montana | 127 | 12
1987 | measles_indigenous | Colorado | 5 | 12
1987 | measles_imported | Massachusetts | 39 | 12
1987 | measles_imported | Connecticut | 6 | 12
1987 | measles_imported | Middle Atlantic | 53 | 12
1987 | measles_imported | Pennsylvania | 13 | 12
1987 | measles_imported | Minnesota | 20 | 12
1987 | measles_imported | South Dakota | - | 12
1987 | measles_imported | Nebraska | - | 12
1987 | measles_imported | Montana | 1 | 12
1987 | measles_imported | Wyoming | 2 | 12
1987 | measles_imported | Colorado | 4 | 12
1987 | measles_imported | New Mexico | 9 | 12
1987 | measles_imported | Utah | 1 | 12
1987 | measles_imported | Nevada | 1 | 12
1987 | measles_imported | Pacific | 115 | 12
1987 | measles_imported | Washington | 13 | 12
1987 | pertussis | Massachusetts | 153 | 12
1987 | pertussis | Connecticut | 31 | 12
1987 | pertussis | Middle Atlantic | 327 | 12
1987 | pertussis | Pennsylvania | 105 | 12
1987 | pertussis | Minnesota | 17 | 12
1987 | pertussis | Montana | 8 | 12
1987 | pertussis | Idaho | 91 | 12
1987 | pertussis | Wyoming | 5 | 12
1987 | pertussis | Colorado | 86 | 12
1987 | pertussis | New Mexico | 13 | 12
1987 | pertussis | Utah | 15 | 12
1987 | pertussis | Pacific | 660 | 12
1987 | pertussis | Washington | 110 | 12
1987 | pertussis | California | 217 | 12
1987 | pertussis | Hawaii | 245 | 12
1986 | pertussis | Maine | 1 | 12
1986 | pertussis | NY_UP | 153 | 12
1986 | pertussis | District of Columbia | - | 12
1986 | pertussis | Tennessee | 18 | 12
1986 | pertussis | Mississippi | 1 | 12
1986 | pertussis | Colorado | 84 | 12
1986 | pertussis | New Mexico | 29 | 12
1986 | pertussis | Arizona | 78 | 12
1986 | pertussis | Utah | 44 | 12
1986 | pertussis | Nevada | 4 | 12
1986 | pertussis | Pacific | 534 | 12
1986 | pertussis | Washington | 163 | 12
1986 | pertussis | Oregon | 16 | 12
1986 | pertussis | California | 299 | 12
1986 | pertussis | Alaska | 5 | 12
1986 | pertussis | Hawaii | 51 | 12
1986 | measles_indigenous | Vermont | - | 12
1986 | measles_indigenous | NY_UP | 74 | 12
1986 | measles_indigenous | Ohio | - | 12
1986 | measles_indigenous | South Dakota | - | 12
1986 | measles_indigenous | Nebraska | - | 12
1986 | measles_indigenous | South Atlantic | 841 | 12
1986 | measles_indigenous | Maryland | 26 | 12
1986 | measles_indigenous | District of Columbia | - | 12
1986 | measles_indigenous | North Carolina | 3 | 12
1986 | measles_indigenous | Florida | 393 | 12
1986 | measles_indigenous | East South Central | 61 | 12
1986 | measles_indigenous | Kentucky | - | 12
1986 | measles_indigenous | Tennessee | 55 | 12
1986 | measles_indigenous | Mississippi | 5 | 12
1986 | measles_indigenous | Mountain | 302 | 12
1986 | measles_indigenous | Montana | - | 12
1986 | measles_indigenous | Idaho | 1 | 12
1986 | measles_indigenous | Wyoming | - | 12
1986 | measles_indigenous | California | 455 | 12
1986 | measles_indigenous | Alaska | - | 12
1986 | measles_indigenous | Hawaii | 27 | 12
1986 | measles_imported | United States | 327* | 12
1986 | measles_imported | New Hampshire | - | 12
1986 | measles_imported | Vermont | - | 12
1986 | measles_imported | Massachusetts | 13 | 12
1986 | measles_imported | Rhode Island | - | 12
1986 | measles_imported | Connecticut | 2 | 12
1986 | measles_imported | NY_UP | 29 | 12
1986 | measles_imported | Illinois | 6 | 12
1986 | measles_imported | Michigan | - | 12
1986 | measles_imported | Wisconsin | 3 | 12
1986 | measles_imported | South Dakota | - | 12
1986 | measles_imported | Nebraska | 1 | 12
1986 | measles_imported | South Atlantic | 57 | 12
1986 | measles_imported | Delaware | - | 12
1986 | measles_imported | Maryland | 9 | 12
1986 | measles_imported | West Virginia | - | 12
1986 | measles_imported | North Carolina | 1 | 12
1986 | measles_imported | South Carolina | - | 12
1986 | measles_imported | Florida | 7 | 12
1986 | measles_imported | Tennessee | 1 | 12
1986 | measles_imported | Mississippi | 1 | 12
1986 | measles_imported | Louisiana | - | 12
1986 | measles_imported | Oklahoma | - | 12
1986 | measles_imported | Texas | 34 | 12
1986 | measles_imported | Idaho | - | 12
1986 | measles_imported | Wyoming | - | 12
1986 | measles_imported | Colorado | 8 | 12
1986 | measles_imported | New Mexico | 7 | 12
1986 | measles_imported | Arizona | 6 | 12
1986 | measles_imported | Utah | - | 12
1986 | measles_imported | Nevada | - | 12
1986 | measles_imported | Oregon | 6 | 12
1986 | measles_imported | California | 31 | 12
1986 | measles_imported | Alaska | - | 12
1986 | measles_imported | Hawaii | 10 | 12
1985 | measles_indigenous | East South Central | - | 12
1984 | pertussis | United States | 2,276 | 16
1983 | measles_indigenous | Arkansas | 5 | 21
1983 | measles_imported | Minnesota | - | 21
1983 | measles_imported | Arkansas | 8 | 21
1983 | measles_imported | Montana | 4 | 21
1983 | measles_imported | Idaho | 10 | 21
1983 | measles_imported | Wyoming | 1 | 21
1983 | measles_imported | Colorado | 3 | 21
1983 | pertussis | Maine | 5 | 21
1983 | pertussis | New Hampshire | 10 | 21
1983 | pertussis | Rhode Island | 5 | 21
1983 | pertussis | Minnesota | 49 | 21
1983 | pertussis | North Dakota | 3 | 21
1983 | pertussis | Delaware | 5 | 21
1983 | pertussis | Georgia | 70 | 21
1983 | pertussis | Tennessee | 8 | 21
1983 | pertussis | Alabama | 5 | 21
1983 | pertussis | Arkansas | 28 | 21
1983 | pertussis | Montana | 2 | 21
1983 | pertussis | Idaho | 16 | 21
1983 | pertussis | Wyoming | 6 | 21
1983 | pertussis | Colorado | 138 | 21
1983 | pertussis | New Mexico | 13 | 21
1982 | measles | Maine | - | 16
1982 | measles | Vermont | 2 | 16
1982 | measles | Rhode Island | - | 16
1982 | measles | Pennsylvania | 7 | 16
1982 | measles | Minnesota | - | 16
1982 | measles | Iowa | - | 16
1982 | measles | North Dakota | - | 16
1982 | measles | South Dakota | - | 16
1982 | measles | South Atlantic | 271 | 16
1982 | measles | Delaware | - | 16
1982 | measles | South Carolina | - | 16
1982 | measles | Georgia | - | 16
1982 | measles | East South Central | 15 | 16
1982 | measles | Mississippi | 6 | 16
1982 | measles | Arkansas | - | 16
1982 | measles | Montana | - | 16
1982 | measles | Idaho | - | 16
1982 | measles | New Mexico | - | 16
1982 | measles | Nevada | - | 16
1982 | pertussis | Vermont | 2 | 16
1982 | pertussis | Pennsylvania | 204 | 16
1982 | pertussis | North Dakota | - | 16
1982 | pertussis | South Atlantic | 302 | 16
1982 | pertussis | District of Columbia | - | 16
1982 | pertussis | South Carolina | 16 | 16
1982 | pertussis | Georgia | 43 | 16
1982 | pertussis | East South Central | 54 | 16
1982 | pertussis | Mississippi | 16 | 16
1982 | pertussis | Nevada | - | 16
1982 | pertussis | Alaska | - | 16
# 1981 pertussis, p.81 ("PERTUSSIS (Whooping cough) - by area and age", Total
# column). The OCR layer mixes this column with its neighbours, so every cell
# below the US row was read from the image.
1981 | pertussis | New England | 49 | 81
1981 | pertussis | Maine | 13 | 81
1981 | pertussis | New Hampshire | 8 | 81
1981 | pertussis | Vermont | - | 81
1981 | pertussis | Massachusetts | 15 | 81
1981 | pertussis | Rhode Island | 11 | 81
1981 | pertussis | Connecticut | 2 | 81
1981 | pertussis | Middle Atlantic | 169 | 81
1981 | pertussis | NY_UP | 97 | 81
1981 | pertussis | NY_CITY | 25 | 81
1981 | pertussis | New Jersey | 12 | 81
1981 | pertussis | Pennsylvania | 35 | 81
1981 | pertussis | East North Central | 281 | 81
1981 | pertussis | Ohio | 43 | 81
1981 | pertussis | Indiana | 87 | 81
1981 | pertussis | Illinois | 88 | 81
1981 | pertussis | Michigan | 30 | 81
1981 | pertussis | Wisconsin | 33 | 81
1981 | pertussis | West North Central | 66 | 81
1981 | pertussis | Minnesota | 16 | 81
1981 | pertussis | Iowa | 9 | 81
1981 | pertussis | Missouri | 24 | 81
1981 | pertussis | North Dakota | 1 | 81
1981 | pertussis | South Dakota | 2 | 81
1981 | pertussis | Nebraska | 6 | 81
1981 | pertussis | Kansas | 8 | 81
1981 | pertussis | South Atlantic | 177 | 81
1981 | pertussis | Delaware | 2 | 81
1981 | pertussis | Maryland | 1 | 81
1981 | pertussis | District of Columbia | - | 81
1981 | pertussis | Virginia | 10 | 81
1981 | pertussis | West Virginia | 6 | 81
1981 | pertussis | North Carolina | 12 | 81
1981 | pertussis | South Carolina | 11 | 81
1981 | pertussis | Georgia | 57 | 81
1981 | pertussis | Florida | 78 | 81
1981 | pertussis | East South Central | 49 | 81
1981 | pertussis | Kentucky | 25 | 81
1981 | pertussis | Tennessee | 16 | 81
1981 | pertussis | Alabama | - | 81
1981 | pertussis | Mississippi | 8 | 81
1981 | pertussis | West South Central | 106 | 81
1981 | pertussis | Arkansas | 5 | 81
1981 | pertussis | Louisiana | 8 | 81
1981 | pertussis | Oklahoma | 2 | 81
1981 | pertussis | Texas | 91 | 81
1981 | pertussis | Mountain | 86 | 81
1981 | pertussis | Montana | 12 | 81
1981 | pertussis | Idaho | 4 | 81
1981 | pertussis | Wyoming | 7 | 81
1981 | pertussis | Colorado | 24 | 81
1981 | pertussis | New Mexico | 16 | 81
1981 | pertussis | Arizona | 13 | 81
1981 | pertussis | Utah | 8 | 81
1981 | pertussis | Nevada | 2 | 81
1981 | pertussis | Pacific | 265 | 81
1981 | pertussis | Washington | 58 | 81
1981 | pertussis | Oregon | 18 | 81
1981 | pertussis | California | 185 | 81
1981 | pertussis | Alaska | 1 | 81
1981 | pertussis | Hawaii | 3 | 81
# 1981 measles, p.70 ("MEASLES (Rubeola) - by area and month", Total column).
# The scan is curved and the OCR layer lost most row labels; every cell below
# the US row was read from the image, in table order within each division.
1981 | measles | New England | 86 | 70
1981 | measles | Maine | 5 | 70
1981 | measles | New Hampshire | 9 | 70
1981 | measles | Vermont | 3 | 70
1981 | measles | Massachusetts | 59 | 70
1981 | measles | Rhode Island | - | 70
1981 | measles | Connecticut | 10 | 70
1981 | measles | Middle Atlantic | 1,159 | 70
1981 | measles | NY_UP | 228 | 70
1981 | measles | NY_CITY | 108 | 70
1981 | measles | New Jersey | 61 | 70
1981 | measles | Pennsylvania | 762 | 70
1981 | measles | East North Central | 90 | 70
1981 | measles | Ohio | 20 | 70
1981 | measles | Indiana | 9 | 70
1981 | measles | Illinois | 24 | 70
1981 | measles | Michigan | 34 | 70
1981 | measles | Wisconsin | 3 | 70
1981 | measles | West North Central | 10 | 70
1981 | measles | Minnesota | 3 | 70
1981 | measles | Iowa | 1 | 70
1981 | measles | Missouri | 1 | 70
1981 | measles | North Dakota | - | 70
1981 | measles | South Dakota | - | 70
1981 | measles | Nebraska | 4 | 70
1981 | measles | Kansas | 1 | 70
1981 | measles | South Atlantic | 494 | 70
1981 | measles | Delaware | - | 70
1981 | measles | Maryland | 5 | 70
1981 | measles | District of Columbia | 1 | 70
1981 | measles | Virginia | 18 | 70
1981 | measles | West Virginia | 9 | 70
1981 | measles | North Carolina | 3 | 70
1981 | measles | South Carolina | 2 | 70
1981 | measles | Georgia | 111 | 70
1981 | measles | Florida | 345 | 70
1981 | measles | East South Central | 6 | 70
1981 | measles | Kentucky | 2 | 70
1981 | measles | Tennessee | 2 | 70
1981 | measles | Alabama | 2 | 70
1981 | measles | Mississippi | - | 70
1981 | measles | West South Central | 886 | 70
1981 | measles | Arkansas | 25 | 70
1981 | measles | Louisiana | 4 | 70
1981 | measles | Oklahoma | 6 | 70
1981 | measles | Texas | 851 | 70
1981 | measles | Mountain | 39 | 70
1981 | measles | Montana | - | 70
1981 | measles | Idaho | 1 | 70
1981 | measles | Wyoming | 1 | 70
1981 | measles | Colorado | 11 | 70
1981 | measles | New Mexico | 9 | 70
1981 | measles | Arizona | 7 | 70
1981 | measles | Utah | - | 70
1981 | measles | Nevada | 10 | 70
1981 | measles | Pacific | 354 | 70
1981 | measles | Washington | 3 | 70
1981 | measles | Oregon | 5 | 70
1981 | measles | California | 339 | 70
1981 | measles | Alaska | - | 70
1981 | measles | Hawaii | 7 | 70
# 1980, p.19. The US measles cell is printed "13,506" with footnote 2
# ("Includes 38 imported cases"); the OCR layer read it as "13.5062".
1980 | measles | United States | 13,506 | 19
1980 | measles | New England | 677 | 19
1980 | measles | Middle Atlantic | 3,940 | 19
1980 | measles | NY_UP | 735 | 19
1980 | measles | East North Central | 2,459 | 19
1980 | measles | North Dakota | - | 19
1980 | measles | South Dakota | - | 19
1980 | pertussis | New England | 49 | 19
1980 | pertussis | Middle Atlantic | 256 | 19
1980 | pertussis | NY_UP | 160 | 19
1980 | pertussis | East North Central | 474 | 19
1980 | pertussis | North Dakota | 7 | 19
1980 | pertussis | South Dakota | 3 | 19
# 1979, p.13. US measles printed "13,597" with footnote 2 ("Includes 28
# imported cases"); OCR read "13.5972". Division labels lost in the OCR layer.
1979 | measles | United States | 13,597 | 13
1979 | measles | New England | 292 | 13
1979 | measles | Middle Atlantic | 1,648 | 13
1979 | measles | East North Central | 3,645 | 13
1979 | measles | Indiana | 228 | 13
1979 | measles | West North Central | 1,846 | 13
1979 | measles | South Atlantic | 2,194 | 13
1979 | measles | District of Columbia | - | 13
1979 | measles | Virginia | 288 | 13
1979 | measles | East South Central | 278 | 13
1979 | measles | Kentucky | 60 | 13
1979 | measles | Tennessee | 69 | 13
1979 | measles | West South Central | 987 | 13
1979 | measles | Mountain | 341 | 13
1979 | measles | New Mexico | 38 | 13
1979 | measles | Arizona | 80 | 13
1979 | measles | Pacific | 2,366 | 13
1979 | measles | Oregon | 66 | 13
1979 | pertussis | New England | 56 | 13
1979 | pertussis | Middle Atlantic | 152 | 13
1979 | pertussis | East North Central | 588 | 13
1979 | pertussis | Indiana | 41 | 13
1979 | pertussis | West North Central | 59 | 13
1979 | pertussis | South Atlantic | 234 | 13
1979 | pertussis | District of Columbia | - | 13
1979 | pertussis | Virginia | 16 | 13
1979 | pertussis | East South Central | 72 | 13
1979 | pertussis | Kentucky | 30 | 13
1979 | pertussis | Tennessee | 31 | 13
1979 | pertussis | West South Central | 173 | 13
1979 | pertussis | Mountain | 123 | 13
1979 | pertussis | Montana | 15 | 13
1979 | pertussis | Colorado | 42 | 13
1979 | pertussis | New Mexico | 30 | 13
1979 | pertussis | Arizona | 30 | 13
1979 | pertussis | Pacific | 166 | 13
1979 | pertussis | Oregon | 11 | 13
1976 | measles | Idaho | 2,024 | 11
1975 | measles | Connecticut | 129 | 10
# printed "635" with a small raised speck before it (OCR "•635")
1975 | measles | West South Central | 635 | 10
1974 | measles | California | 1,115 | 10
# 1968 and 1969, p.10 (Table 6). Mississippi's measles cell is printed with an
# asterisk: "*Includes rubella" (footnote on the same page). Recorded as "n*".
1968 | measles | New Hampshire | 150 | 10
1968 | measles | Mississippi | 248* | 10
1968 | measles | Alaska | 11 | 10
1968 | pertussis | Alaska | 3 | 10
1969 | measles | Mississippi | 221* | 10
# 1970 pertussis, p.10. New York City and Virginia are both printed "163"
# followed by a small unexplained stroke; there is no footnote on the page.
# They are NOT entered here (awaiting an editor decision), so 1970 pertussis
# stays out. With both read as 163 the year passes the division test.
1970 | pertussis | New Jersey | - | 10
1970 | pertussis | Kansas | - | 10
1970 | pertussis | Oklahoma | 45 | 10
1970 | pertussis | Wyoming | - | 10
1970 | pertussis | Nevada | - | 10
# 1971, p.10 (the OCR layer lost the Arkansas, Georgia, New Jersey, Oregon and
# Virginia rows)
1971 | measles | Arkansas | 819 | 10
1971 | measles | Georgia | 390 | 10
1971 | measles | New Jersey | 1,260 | 10
1971 | measles | Oregon | 388 | 10
1971 | measles | Virginia | 1,628 | 10
1971 | pertussis | Arkansas | 51 | 10
1971 | pertussis | Georgia | 18 | 10
1971 | pertussis | New Jersey | 7 | 10
1971 | pertussis | Oregon | 108 | 10
1971 | pertussis | Virginia | 61 | 10
1971 | pertussis | East South Central | 377 | 10
1971 | pertussis | Hawaii | - | 10
1957 | pertussis | East South Central | 1,921 | 10
# 1958, p.10: the first digit of the Pacific total is faintly printed; at
# 800 dpi it is a 5 (OCR "f,393")
1958 | pertussis | Pacific | 5,393 | 10
1959 | pertussis | Alaska | - | 11
# 1956, p.10 (one New York row; Alaska and Hawaii not in the table)
1956 | pertussis | New York | 2,248 | 10
1956 | pertussis | Illinois | 569 | 10
1956 | pertussis | Michigan | 1,907 | 10
1956 | pertussis | Wisconsin | 982 | 10
1956 | pertussis | Minnesota | 123 | 10
1956 | pertussis | Maryland | 179 | 10
1956 | pertussis | West Virginia | 297 | 10
# printed "780" with a small raised speck before it (OCR "•780")
1956 | pertussis | Arizona | 780 | 10
# 1960 pertussis, p.9, whole column from the image (one New York row)
1960 | pertussis | United States | 14,809 | 9
1960 | pertussis | New England | 821 | 9
1960 | pertussis | Maine | 173 | 9
1960 | pertussis | New Hampshire | 103 | 9
1960 | pertussis | Vermont | 45 | 9
1960 | pertussis | Massachusetts | 226 | 9
1960 | pertussis | Rhode Island | 43 | 9
1960 | pertussis | Connecticut | 231 | 9
1960 | pertussis | Middle Atlantic | 1,297 | 9
1960 | pertussis | New York | 734 | 9
1960 | pertussis | New Jersey | 226 | 9
1960 | pertussis | Pennsylvania | 337 | 9
1960 | pertussis | East North Central | 2,215 | 9
1960 | pertussis | Ohio | 127 | 9
1960 | pertussis | Indiana | 290 | 9
1960 | pertussis | Illinois | 442 | 9
1960 | pertussis | Michigan | 1,129 | 9
1960 | pertussis | Wisconsin | 227 | 9
1960 | pertussis | West North Central | 457 | 9
1960 | pertussis | Minnesota | 22 | 9
1960 | pertussis | Iowa | 115 | 9
1960 | pertussis | Missouri | 71 | 9
1960 | pertussis | North Dakota | 56 | 9
1960 | pertussis | South Dakota | 66 | 9
1960 | pertussis | Nebraska | 66 | 9
1960 | pertussis | Kansas | 61 | 9
1960 | pertussis | South Atlantic | 1,387 | 9
1960 | pertussis | Delaware | 24 | 9
1960 | pertussis | Maryland | 120 | 9
1960 | pertussis | District of Columbia | 52 | 9
1960 | pertussis | Virginia | 344 | 9
1960 | pertussis | West Virginia | 164 | 9
1960 | pertussis | North Carolina | 111 | 9
1960 | pertussis | South Carolina | 128 | 9
1960 | pertussis | Georgia | 21 | 9
1960 | pertussis | Florida | 423 | 9
1960 | pertussis | East South Central | 1,595 | 9
1960 | pertussis | Kentucky | 336 | 9
1960 | pertussis | Tennessee | 1,111 | 9
1960 | pertussis | Alabama | 104 | 9
1960 | pertussis | Mississippi | 44 | 9
1960 | pertussis | West South Central | 2,705 | 9
1960 | pertussis | Arkansas | 54 | 9
1960 | pertussis | Louisiana | 14 | 9
1960 | pertussis | Oklahoma | 103 | 9
1960 | pertussis | Texas | 2,534 | 9
1960 | pertussis | Mountain | 1,586 | 9
1960 | pertussis | Montana | 301 | 9
1960 | pertussis | Idaho | 107 | 9
1960 | pertussis | Wyoming | 27 | 9
1960 | pertussis | Colorado | 448 | 9
1960 | pertussis | New Mexico | 50 | 9
1960 | pertussis | Arizona | 398 | 9
1960 | pertussis | Utah | 249 | 9
1960 | pertussis | Nevada | 6 | 9
1960 | pertussis | Pacific | 2,746 | 9
1960 | pertussis | Washington | 251 | 9
1960 | pertussis | Oregon | 534 | 9
1960 | pertussis | California | 1,957 | 9
1960 | pertussis | Alaska | 4 | 9
1960 | pertussis | Hawaii | - | 9
# 1961 pertussis, p.10
1961 | pertussis | Maine | 220 | 10
# printed "337" with a small dot before it (OCR ".337")
1961 | pertussis | New Jersey | 337 | 10
1961 | pertussis | Kansas | - | 10
1961 | pertussis | Alabama | 64 | 10
1961 | pertussis | Arkansas | 33 | 10
1961 | pertussis | Oklahoma | 16 | 10
1961 | pertussis | Texas | 1,365 | 10
1961 | pertussis | Montana | 92 | 10
1961 | pertussis | Washington | 344 | 10
1962 | pertussis | Montana | 70 | 10
1963 | pertussis | New Jersey | - | 10
1963 | pertussis | Iowa | 149 | 10
1963 | pertussis | Tennessee | 865 | 10
1963 | pertussis | Alabama | 142 | 10
1963 | pertussis | Alaska | 17 | 10
1964 | pertussis | New Mexico | 49 | 12
1965 | pertussis | United States | 6,799 | 10
1965 | pertussis | Kentucky | 68 | 10
1965 | pertussis | Alabama | 57 | 10
1965 | pertussis | Arkansas | 25 | 10
1965 | pertussis | Louisiana | 4 | 10
1965 | pertussis | Colorado | 98 | 10
1965 | pertussis | New Mexico | 6 | 10
1965 | pertussis | Utah | 51 | 10
1965 | pertussis | Alaska | 9 | 10
1966 | pertussis | Alaska | - | 10
1967 | pertussis | Maine | 265 | 10
1967 | pertussis | Texas | 846 | 10
1967 | pertussis | Montana | 199 | 10
#END
"""
for _ln in _MP_IMAGE.strip().splitlines():
    if _ln.startswith("#"):
        continue
    _y, _d, _a, _t, _p = [x.strip() for x in _ln.split("|")]
    _a = {"NY_UP": NY_UP, "NY_CITY": NY_CITY}.get(_a, _a)
    SCAN_IMAGE_CELLS[(int(_y), _d, _a)] = (_t, int(_p))

# Measles 1956-1967 cells read from the page image (same rules as above). 1960 is a
# whole column (the page's text layer has no usable rows). In 1956-1958 Nebraska and
# 1957 Mississippi carry a superscript footnote number, which is not part of the count.
_M6467_IMAGE = """
# year | disease | area | text on the image | PDF page
1964 | measles | NY_UP | 13,124 | 11
1964 | measles | South Carolina | 4,269† | 11
1964 | measles | New Mexico | 1,181 | 11
1964 | measles | Arizona | 6,767 | 11
1964 | measles | Utah | 2,435 | 11
1965 | measles | Rhode Island | 3,973 | 10
1966 | measles | Hawaii | 168 | 10
1967 | measles | Maine | 278 | 10
1967 | measles | Texas | 13,411 | 10
1967 | measles | Montana | 340 | 10
1956 | measles | Rhode Island | 254 | 8
1956 | measles | Nebraska | 2,289 | 8
1956 | measles | Pacific | 48,125 | 8
1956 | measles | Washington | 12,862 | 8
1957 | measles | Ohio | 8,627 | 8
1957 | measles | Nebraska | 322 | 8
1957 | measles | Kansas | * | 8
1957 | measles | Mississippi | 1,290 | 8
1957 | measles | Montana | 3,746 | 8
1958 | measles | New Hampshire | 4,711 | 8
1958 | measles | Ohio | 31,444 | 8
1958 | measles | Nebraska | 1,519 | 8
1958 | measles | Mississippi | 1,549 | 8
1958 | measles | Oklahoma | 7,500 | 8
1959 | measles | Pennsylvania | 32,195 | 9
1959 | measles | Indiana | 5,279 | 9
1959 | measles | Wisconsin | 16,559 | 9
1959 | measles | Minnesota | 2,844 | 9
1959 | measles | Kentucky | 7,037 | 9
1959 | measles | Mississippi | 1,952 | 9
1959 | measles | Arkansas | 898 | 9
1959 | measles | New Mexico | 4,735 | 9
1960 | measles | United States | 441,703 | 9
1960 | measles | New England | 44,355 | 9
1960 | measles | Maine | 3,538 | 9
1960 | measles | New Hampshire | 1,929 | 9
1960 | measles | Vermont | 3,266 | 9
1960 | measles | Massachusetts | 22,403 | 9
1960 | measles | Rhode Island | 1,892 | 9
1960 | measles | Connecticut | 11,327 | 9
1960 | measles | Middle Atlantic | 64,347 | 9
1960 | measles | New York | 46,443 | 9
1960 | measles | New Jersey | 10,559 | 9
1960 | measles | Pennsylvania | 7,345 | 9
1960 | measles | East North Central | 131,527 | 9
1960 | measles | Ohio | 18,170 | 9
1960 | measles | Indiana | 10,225 | 9
1960 | measles | Illinois | 22,448 | 9
1960 | measles | Michigan | 36,161 | 9
1960 | measles | Wisconsin | 44,523 | 9
1960 | measles | West North Central | 9,862 | 9
1960 | measles | Minnesota | 4,203 | 9
1960 | measles | Iowa | 1,790 | 9
1960 | measles | Missouri | 799 | 9
1960 | measles | North Dakota | 2,774 | 9
1960 | measles | South Dakota | 79 | 9
1960 | measles | Nebraska | 217 | 9
1960 | measles | Kansas | NN | 9
1960 | measles | South Atlantic | 24,007 | 9
1960 | measles | Delaware | 656 | 9
1960 | measles | Maryland | 3,202 | 9
1960 | measles | District of Columbia | 1,197 | 9
1960 | measles | Virginia | 7,595 | 9
1960 | measles | West Virginia | 3,812 | 9
1960 | measles | North Carolina | 1,417 | 9
1960 | measles | South Carolina | 1,799 | 9
1960 | measles | Georgia | 236 | 9
1960 | measles | Florida | 4,093 | 9
1960 | measles | East South Central | 34,719 | 9
1960 | measles | Kentucky | 11,367 | 9
1960 | measles | Tennessee | 19,202 | 9
1960 | measles | Alabama | 2,069 | 9
1960 | measles | Mississippi | 2,081 | 9
1960 | measles | West South Central | 53,582 | 9
1960 | measles | Arkansas | 1,410 | 9
1960 | measles | Louisiana | 266 | 9
1960 | measles | Oklahoma | 1,232 | 9
1960 | measles | Texas | 50,674 | 9
1960 | measles | Mountain | 25,604 | 9
1960 | measles | Montana | 2,438 | 9
1960 | measles | Idaho | 3,227 | 9
1960 | measles | Wyoming | 716 | 9
1960 | measles | Colorado | 6,794 | 9
1960 | measles | New Mexico | 1,901 | 9
1960 | measles | Arizona | 4,863 | 9
1960 | measles | Utah | 4,908 | 9
1960 | measles | Nevada | 757 | 9
1960 | measles | Pacific | 53,700 | 9
1960 | measles | Washington | 13,678 | 9
1960 | measles | Oregon | 11,104 | 9
1960 | measles | California | 22,684 | 9
1960 | measles | Alaska | 1,260 | 9
1960 | measles | Hawaii | 4,974 | 9
1961 | measles | Louisiana | 48 | 9
1961 | measles | Texas | 16,697 | 9
1961 | measles | Montana | 2,484 | 9
1961 | measles | Idaho | 2,051 | 9
1961 | measles | Wyoming | 493 | 9
1961 | measles | Colorado | 4,046 | 9
1961 | measles | New Mexico | 914 | 9
1961 | measles | Arizona | 8,570 | 9
1961 | measles | Utah | 1,711 | 9
1961 | measles | Nevada | 685 | 9
1961 | measles | Oregon | 5,939 | 9
1962 | measles | Maine | 7,135 | 9
1962 | measles | Vermont | 2,040 | 9
1962 | measles | Minnesota | 1,675 | 9
1962 | measles | West Virginia | 10,007 | 9
1962 | measles | South Carolina | 930 | 9
1962 | measles | Alabama | 2,423 | 9
1962 | measles | Mississippi | 2,757 | 9
1962 | measles | Louisiana | 252 | 9
1962 | measles | Oklahoma | 2,095 | 9
1962 | measles | Texas | 66,915 | 9
1962 | measles | Mountain | 32,340 | 9
1962 | measles | Montana | 8,662 | 9
1962 | measles | Idaho | 1,688 | 9
1962 | measles | Wyoming | 491 | 9
1962 | measles | Colorado | 9,001 | 9
1962 | measles | New Mexico | 1,451 | 9
1962 | measles | Arizona | 6,305 | 9
1962 | measles | Utah | 4,067 | 9
1962 | measles | Nevada | 675 | 9
1962 | measles | Pacific | 69,074 | 9
1962 | measles | Washington | 22,060 | 9
1962 | measles | Oregon | 13,868 | 9
1962 | measles | California | 28,585 | 9
1962 | measles | Alaska | 1,386 | 9
1962 | measles | Hawaii | 3,175 | 9
1963 | measles | Vermont | 1,928 | 9
1963 | measles | Massachusetts | 4,978 | 9
1963 | measles | Minnesota | 3,368 | 9
1963 | measles | Maryland | 2,274 | 9
1963 | measles | West Virginia | 14,273 | 9
1963 | measles | North Carolina | 1,607 | 9
1963 | measles | Georgia | 226 | 9
1963 | measles | Tennessee | 7,880 | 9
1963 | measles | Alabama | 1,336 | 9
1963 | measles | Wyoming | 824 | 9
1963 | measles | Colorado | 7,137 | 9
1963 | measles | New Mexico | 815 | 9
1963 | measles | Utah | 3,400 | 9
1963 | measles | Pacific | 41,870 | 9
1963 | measles | Hawaii | 3,623 | 9
"""
for _ln in _M6467_IMAGE.strip().splitlines():
    if _ln.startswith("#"):
        continue
    _y, _d, _a, _t, _p = [x.strip() for x in _ln.split("|")]
    _a = {"NY_UP": NY_UP, "NY_CITY": NY_CITY}.get(_a, _a)
    SCAN_IMAGE_CELLS[(int(_y), _d, _a)] = (_t, int(_p))

# Hepatitis A cells read from the page image (same rules as above). The column is
# "Hepatitis, infectious" in 1966-1971, "Infectious (A)" in 1972 and "Hepatitis A"
# from 1973. New York City carries a footnote mark in 1977-1984 (its cases were
# typed by a blood test); 1986 New York City is printed "NA".
_HA_IMAGE = """
# year | disease | area | text on the image | PDF page
1966 | hepatitis_a | Ohio | 1,344 | 9
1967 | hepatitis_a | United States | 38,909 | 9
1967 | hepatitis_a | New England | 1,750 | 9
1967 | hepatitis_a | Maine | 171 | 9
1967 | hepatitis_a | New Hampshire | 44 | 9
1967 | hepatitis_a | Vermont | 16 | 9
1967 | hepatitis_a | Massachusetts | 716 | 9
1967 | hepatitis_a | Rhode Island | 195 | 9
1967 | hepatitis_a | Connecticut | 608 | 9
1967 | hepatitis_a | Middle Atlantic | 6,154 | 9
1967 | hepatitis_a | NY_CITY | 1,965 | 9
1967 | hepatitis_a | NY_UP | 1,444 | 9
1967 | hepatitis_a | New Jersey | 1,260 | 9
1967 | hepatitis_a | Pennsylvania | 1,485 | 9
1967 | hepatitis_a | East North Central | 6,161 | 9
1967 | hepatitis_a | Ohio | 1,422 | 9
1967 | hepatitis_a | Indiana | 618 | 9
1967 | hepatitis_a | Illinois | 1,763 | 9
1967 | hepatitis_a | Michigan | 1,882 | 9
1967 | hepatitis_a | Wisconsin | 476 | 9
1967 | hepatitis_a | West North Central | 2,549 | 9
1967 | hepatitis_a | Minnesota | 511 | 9
1967 | hepatitis_a | Iowa | 350 | 9
1967 | hepatitis_a | Missouri | 1,307 | 9
1967 | hepatitis_a | North Dakota | 77 | 9
1967 | hepatitis_a | South Dakota | 14 | 9
1967 | hepatitis_a | Nebraska | 72 | 9
1967 | hepatitis_a | Kansas | 218 | 9
1967 | hepatitis_a | South Atlantic | 4,231 | 9
1967 | hepatitis_a | Delaware | 176 | 9
1967 | hepatitis_a | Maryland | 879 | 9
1967 | hepatitis_a | District of Columbia | 45 | 9
1967 | hepatitis_a | Virginia | 744 | 9
1967 | hepatitis_a | West Virginia | 383 | 9
1967 | hepatitis_a | North Carolina | 338 | 9
1967 | hepatitis_a | South Carolina | 111 | 9
1967 | hepatitis_a | Georgia | 916 | 9
1967 | hepatitis_a | Florida | 639 | 9
1967 | hepatitis_a | East South Central | 2,746 | 9
1967 | hepatitis_a | Kentucky | 1,135 | 9
1967 | hepatitis_a | Tennessee | 835 | 9
1967 | hepatitis_a | Alabama | 293 | 9
1967 | hepatitis_a | Mississippi | 483 | 9
1967 | hepatitis_a | West South Central | 4,083 | 9
1967 | hepatitis_a | Arkansas | 285 | 9
1967 | hepatitis_a | Louisiana | 652* | 9
1967 | hepatitis_a | Oklahoma | 345 | 9
1967 | hepatitis_a | Texas | 2,801 | 9
1967 | hepatitis_a | Mountain | 1,794 | 9
1967 | hepatitis_a | Montana | 185 | 9
1967 | hepatitis_a | Idaho | 131 | 9
1967 | hepatitis_a | Wyoming | 70 | 9
1967 | hepatitis_a | Colorado | 328 | 9
1967 | hepatitis_a | New Mexico | 446 | 9
1967 | hepatitis_a | Arizona | 416 | 9
1967 | hepatitis_a | Utah | 169 | 9
1967 | hepatitis_a | Nevada | 49 | 9
1967 | hepatitis_a | Pacific | 9,441 | 9
1967 | hepatitis_a | Washington | 983 | 9
1967 | hepatitis_a | Oregon | 864 | 9
1967 | hepatitis_a | California | 7,499 | 9
1967 | hepatitis_a | Alaska | 41 | 9
1967 | hepatitis_a | Hawaii | 54 | 9
1968 | hepatitis_a | Pennsylvania | 1,831 | 9
1968 | hepatitis_a | North Carolina | 375 | 9
1968 | hepatitis_a | Kentucky | 1,152 | 9
1968 | hepatitis_a | Louisiana | *751 | 9
1969 | hepatitis_a | Louisiana | *873 | 9
1970 | hepatitis_a | Ohio | 2,280 | 9
1970 | hepatitis_a | South Atlantic | 6,751 | 9
1970 | hepatitis_a | South Carolina | 358 | 9
1970 | hepatitis_a | East South Central | 3,229 | 9
1970 | hepatitis_a | West South Central | 4,206 | 9
1970 | hepatitis_a | Mountain | 3,217 | 9
1970 | hepatitis_a | Nevada | 192 | 9
1970 | hepatitis_a | Pacific | 12,781 | 9
1970 | hepatitis_a | Oregon | 1,033 | 9
1970 | hepatitis_a | Hawaii | 233 | 9
1972 | hepatitis_a | Maine | 464 | 9
1972 | hepatitis_a | Florida | 2,459 | 9
1972 | hepatitis_a | Tennessee | 1,435 | 9
1972 | hepatitis_a | Alabama | 382 | 9
1972 | hepatitis_a | Mississippi | 237 | 9
1972 | hepatitis_a | Arkansas | 340 | 9
1972 | hepatitis_a | Louisiana | 630 | 9
1972 | hepatitis_a | Texas | 3,905 | 9
1972 | hepatitis_a | Montana | 258 | 9
1972 | hepatitis_a | Idaho | 383 | 9
1972 | hepatitis_a | Wyoming | 49 | 9
1972 | hepatitis_a | Arizona | 750 | 9
1972 | hepatitis_a | Nevada | 98 | 9
1972 | hepatitis_a | Alaska | 247 | 9
1973 | hepatitis_a | Middle Atlantic | 5,929 | 9
1973 | hepatitis_a | West North Central | 2,047 | 9
1973 | hepatitis_a | West South Central | 7,075 | 9
1973 | hepatitis_a | Mountain | 2,628 | 9
1973 | hepatitis_a | Pacific | 9,960 | 9
1974 | hepatitis_a | District of Columbia | 44 | 9
1975 | hepatitis_a | New England | 1,196 | 9
1975 | hepatitis_a | Ohio | 1,648 | 9
1975 | hepatitis_a | Missouri | 542 | 9
1975 | hepatitis_a | Virginia | 420 | 9
1975 | hepatitis_a | West Virginia | 160 | 9
1975 | hepatitis_a | South Carolina | 340 | 9
1975 | hepatitis_a | Florida | 2,967 | 9
1975 | hepatitis_a | West South Central | 4,215 | 9
1975 | hepatitis_a | Mountain | 1,988 | 9
1975 | hepatitis_a | Wyoming | 30 | 9
1975 | hepatitis_a | Pacific | 7,326 | 9
1977 | hepatitis_a | United States | 31,153 | 11
1977 | hepatitis_a | New England | 667 | 11
1977 | hepatitis_a | Maine | 26 | 11
1977 | hepatitis_a | New Hampshire | 65 | 11
1977 | hepatitis_a | Vermont | 43 | 11
1977 | hepatitis_a | Massachusetts | 145 | 11
1977 | hepatitis_a | Rhode Island | 114 | 11
1977 | hepatitis_a | Connecticut | 274 | 11
1977 | hepatitis_a | Middle Atlantic | 3,169 | 11
1977 | hepatitis_a | NY_UP | 734 | 11
1977 | hepatitis_a | NY_CITY | 566 | 11
1977 | hepatitis_a | New Jersey | 844 | 11
1977 | hepatitis_a | Pennsylvania | 1,025 | 11
1977 | hepatitis_a | East North Central | 5,076 | 11
1977 | hepatitis_a | Ohio | 1,428 | 11
1977 | hepatitis_a | Indiana | 253 | 11
1977 | hepatitis_a | Illinois | 1,424 | 11
1977 | hepatitis_a | Michigan | 1,602 | 11
1977 | hepatitis_a | Wisconsin | 369 | 11
1977 | hepatitis_a | West North Central | 1,661 | 11
1977 | hepatitis_a | Minnesota | 440 | 11
1977 | hepatitis_a | Iowa | 118 | 11
1977 | hepatitis_a | Missouri | 504 | 11
1977 | hepatitis_a | North Dakota | 67 | 11
1977 | hepatitis_a | South Dakota | 34 | 11
1977 | hepatitis_a | Nebraska | 164 | 11
1977 | hepatitis_a | Kansas | 334 | 11
1977 | hepatitis_a | South Atlantic | 4,319 | 11
1977 | hepatitis_a | Delaware | 47 | 11
1977 | hepatitis_a | Maryland | 425 | 11
1977 | hepatitis_a | District of Columbia | 37 | 11
1977 | hepatitis_a | Virginia | 345 | 11
1977 | hepatitis_a | West Virginia | 303 | 11
1977 | hepatitis_a | North Carolina | 442 | 11
1977 | hepatitis_a | South Carolina | 180 | 11
1977 | hepatitis_a | Georgia | 1,165 | 11
1977 | hepatitis_a | Florida | 1,375 | 11
1977 | hepatitis_a | East South Central | 2,363 | 11
1977 | hepatitis_a | Kentucky | 526 | 11
1977 | hepatitis_a | Tennessee | 1,054 | 11
1977 | hepatitis_a | Alabama | 212 | 11
1977 | hepatitis_a | Mississippi | 571 | 11
1977 | hepatitis_a | West South Central | 3,535 | 11
1977 | hepatitis_a | Arkansas | 485 | 11
1977 | hepatitis_a | Louisiana | 517 | 11
1977 | hepatitis_a | Oklahoma | 447 | 11
1977 | hepatitis_a | Texas | 2,086 | 11
1977 | hepatitis_a | Mountain | 2,860 | 11
1977 | hepatitis_a | Montana | 250 | 11
1977 | hepatitis_a | Idaho | 142 | 11
1977 | hepatitis_a | Wyoming | 23 | 11
1977 | hepatitis_a | Colorado | 534 | 11
1977 | hepatitis_a | New Mexico | 547 | 11
1977 | hepatitis_a | Arizona | 1,087 | 11
1977 | hepatitis_a | Utah | 223 | 11
1977 | hepatitis_a | Nevada | 54 | 11
1977 | hepatitis_a | Pacific | 7,503 | 11
1977 | hepatitis_a | Washington | 626 | 11
1977 | hepatitis_a | Oregon | 767 | 11
1977 | hepatitis_a | California | 5,400 | 11
1977 | hepatitis_a | Alaska | 568 | 11
1977 | hepatitis_a | Hawaii | 142 | 11
1978 | hepatitis_a | New England | 817 | 20
1978 | hepatitis_a | NY_CITY | 499 | 20
1978 | hepatitis_a | East North Central | 4,171 | 20
1979 | hepatitis_a | NY_CITY | 386 | 12
1980 | hepatitis_a | NY_CITY | 364 | 18
1980 | hepatitis_a | North Dakota | 57 | 18
1980 | hepatitis_a | South Dakota | 72 | 18
1982 | hepatitis_a | NY_CITY | 689 | 15
1982 | hepatitis_a | Missouri | 204 | 15
1982 | hepatitis_a | District of Columbia | 17 | 15
1982 | hepatitis_a | West Virginia | 91 | 15
1982 | hepatitis_a | South Carolina | 316 | 15
1982 | hepatitis_a | Kentucky | 336 | 15
1982 | hepatitis_a | Tennessee | 346 | 15
1983 | hepatitis_a | NY_UP | 344 | 20
1983 | hepatitis_a | NY_CITY | 507 | 20
1984 | hepatitis_a | NY_CITY | 560 | 15
1984 | hepatitis_a | New Jersey | 656 | 15
1984 | hepatitis_a | Indiana | 120 | 15
1984 | hepatitis_a | Illinois | 462 | 15
1984 | hepatitis_a | Michigan | 423 | 15
1984 | hepatitis_a | Wisconsin | 232 | 15
1984 | hepatitis_a | Minnesota | 130 | 15
1984 | hepatitis_a | Iowa | 60 | 15
1984 | hepatitis_a | Delaware | 44 | 15
1984 | hepatitis_a | Maryland | 60 | 15
1984 | hepatitis_a | District of Columbia | 13 | 15
1984 | hepatitis_a | Kentucky | 316 | 15
1984 | hepatitis_a | Tennessee | 110 | 15
1984 | hepatitis_a | Louisiana | 316 | 15
1984 | hepatitis_a | Texas | 2,605 | 15
1985 | hepatitis_a | Indiana | 123 | 11
1985 | hepatitis_a | Pacific | 10,114 | 11
1986 | hepatitis_a | Vermont | 22 | 11
1986 | hepatitis_a | NY_CITY | NA¶ | 11
1986 | hepatitis_a | New Jersey | 383 | 11
1986 | hepatitis_a | Illinois | 342 | 11
1986 | hepatitis_a | Michigan | 289 | 11
1986 | hepatitis_a | South Dakota | 171 | 11
1986 | hepatitis_a | Kansas | 137 | 11
1986 | hepatitis_a | Tennessee | 77 | 11
1986 | hepatitis_a | Colorado | 210 | 11
1986 | hepatitis_a | New Mexico | 567 | 11
1986 | hepatitis_a | Arizona | 1,427 | 11
1986 | hepatitis_a | Utah | 161 | 11
1986 | hepatitis_a | Oregon | 1,898 | 11
1986 | hepatitis_a | Alaska | 108 | 11
1986 | hepatitis_a | Hawaii | 14 | 11
1987 | hepatitis_a | Vermont | 14 | 11
1987 | hepatitis_a | Massachusetts | 342 | 11
1987 | hepatitis_a | NY_UP | 808 | 11
1989 | hepatitis_a | Colorado | 540 | 12
1990 | hepatitis_a | New Jersey | 437 | 18
1990 | hepatitis_a | Nebraska | 104 | 18
1990 | hepatitis_a | District of Columbia | 39 | 18
1990 | hepatitis_a | North Carolina | 649 | 18
1991 | hepatitis_a | Connecticut | 122 | 20
1992 | hepatitis_a | Hawaii | 171 | 22
"""
for _ln in _HA_IMAGE.strip().splitlines():
    if _ln.startswith("#"):
        continue
    _y, _d, _a, _t, _p = [x.strip() for x in _ln.split("|")]
    _a = {"NY_UP": NY_UP, "NY_CITY": NY_CITY}.get(_a, _a)
    SCAN_IMAGE_CELLS[(int(_y), _d, _a)] = (_t, int(_p))

# Paralytic polio, 1956-1992. Two kinds of entry.
# _PP_IMAGE: single cells read from the page image where the OCR layer is damaged
# (1956-1959, 1961, 1963, 1964; same rules as above).
# _PP_COLUMNS: years where the whole "Paralytic" column was read from the page image,
# because the column sits in a table the OCR layer cannot be used for (the tables of
# low-frequency diseases, 1965-1977) or is nearly all dashes that the OCR layer drops.
# Only the cells that are not a dash are listed; every other state and division row
# of that column is a dash on the page (no reported cases). Format per year:
#   page | United States | Division total: State n, State n; Division total: ...
# A superscript footnote number printed on a count (Texas 1977, New Mexico 1978,
# California 1979) is left off; a printed symbol is kept.
_PP_IMAGE = """
# year | disease | area | text on the image | PDF page
1956 | polio_paralytic | Rhode Island | 2 | 8
1956 | polio_paralytic | Kansas | - | 8
1956 | polio_paralytic | Delaware | 11 | 8
1956 | polio_paralytic | Oklahoma | 93 | 8
1956 | polio_paralytic | New Mexico | 37 | 8
1956 | polio_paralytic | Pacific | 1,532 | 8
1956 | polio_paralytic | Washington | 98 | 8
1957 | polio_paralytic | Rhode Island | - | 8
1957 | polio_paralytic | Ohio | 122 | 8
1957 | polio_paralytic | Montana | 5 | 8
1958 | polio_paralytic | New Hampshire | 1 | 8
1958 | polio_paralytic | Ohio | 276 | 8
1958 | polio_paralytic | Mississippi | 42 | 8
1958 | polio_paralytic | Oklahoma | 26 | 8
1959 | polio_paralytic | New England | 353 | 9
1959 | polio_paralytic | Pennsylvania | 165 | 9
1959 | polio_paralytic | Indiana | 109 | 9
1959 | polio_paralytic | Wisconsin | 43 | 9
1959 | polio_paralytic | Minnesota | 200 | 9
1959 | polio_paralytic | Mississippi | 81 | 9
1959 | polio_paralytic | Arkansas | 231 | 9
1959 | polio_paralytic | New Mexico | 24 | 9
1961 | polio_paralytic | Maine | 7 | 9
1961 | polio_paralytic | North Dakota | 1 | 9
1961 | polio_paralytic | Virginia | 14 | 9
1961 | polio_paralytic | Louisiana | 44 | 9
1961 | polio_paralytic | Texas | 37 | 9
1961 | polio_paralytic | Montana | 1 | 9
1961 | polio_paralytic | Idaho | 13 | 9
1961 | polio_paralytic | Wyoming | 1 | 9
1961 | polio_paralytic | Colorado | 11 | 9
1961 | polio_paralytic | New Mexico | 2 | 9
1961 | polio_paralytic | Arizona | 6 | 9
1961 | polio_paralytic | Utah | 4 | 9
1961 | polio_paralytic | Nevada | - | 9
1961 | polio_paralytic | Oregon | 9 | 9
1963 | polio_paralytic | New Hampshire | - | 10
1963 | polio_paralytic | Rhode Island | - | 10
1963 | polio_paralytic | Iowa | - | 10
1963 | polio_paralytic | North Dakota | - | 10
1963 | polio_paralytic | Kansas | - | 10
1963 | polio_paralytic | Delaware | 1 | 10
1963 | polio_paralytic | District of Columbia | 1 | 10
1963 | polio_paralytic | Kentucky | - | 10
1963 | polio_paralytic | Alabama | 49 | 10
1963 | polio_paralytic | Mississippi | 15 | 10
1963 | polio_paralytic | Montana | - | 10
1963 | polio_paralytic | Wyoming | - | 10
1963 | polio_paralytic | New Mexico | - | 10
1963 | polio_paralytic | California | 15 | 10
1963 | polio_paralytic | Alaska | - | 10
1963 | polio_paralytic | Hawaii | - | 10
1964 | polio_paralytic | Montana | - | 12
1964 | polio_paralytic | New Mexico | - | 12
1964 | polio_paralytic | Washington | - | 12
1964 | polio_paralytic | Hawaii | - | 12
"""
for _ln in _PP_IMAGE.strip().splitlines():
    if _ln.startswith("#"):
        continue
    _y, _d, _a, _t, _p = [x.strip() for x in _ln.split("|")]
    SCAN_IMAGE_CELLS[(int(_y), _d, _a)] = (_t, int(_p))

_PP_COLUMNS = {
    1960: "10 | 2,525 | New England 195: Maine 49, New Hampshire 1, Vermont 10, Massachusetts 29, Rhode Island 79, Connecticut 27; "
          "Middle Atlantic 409: New York 213, New Jersey 64, Pennsylvania 132; "
          "East North Central 395: Ohio 89, Indiana 117, Illinois 112, Michigan 56, Wisconsin 21; "
          "West North Central 109: Minnesota 37, Iowa 6, Missouri 38, North Dakota 6, South Dakota 2, Nebraska 11, Kansas 9; "
          "South Atlantic 488: Maryland 147, District of Columbia 5, Virginia 55, West Virginia 51, North Carolina 64, South Carolina 92, Georgia 27, Florida 47; "
          "East South Central 249: Kentucky 127, Tennessee 41, Alabama 24, Mississippi 57; "
          "West South Central 191: Arkansas 27, Louisiana 32, Oklahoma 14, Texas 118; "
          "Mountain 77: Montana 15, Idaho 10, Wyoming 18, Colorado 21, New Mexico 4, Arizona 4, Utah 5; "
          "Pacific 412: Washington 46, Oregon 17, California 340, Alaska 1, Hawaii 8",
    1962: "10 | 762 | New England 13: New Hampshire 3, Vermont 1, Massachusetts 7, Connecticut 2; "
          "Middle Atlantic 79: New York 53, New Jersey 7, Pennsylvania 19; "
          "East North Central 124: Ohio 18, Indiana 24, Illinois 54, Michigan 19, Wisconsin 9; "
          "West North Central 35: Minnesota 7, Iowa 4, Missouri 10, North Dakota 3, South Dakota 2, Nebraska 9; "
          "South Atlantic 77: Maryland 2, District of Columbia 1, Virginia 8, West Virginia 18, North Carolina 13, South Carolina 7, Georgia 18, Florida 10; "
          "East South Central 72: Kentucky 20, Tennessee 8, Alabama 21, Mississippi 23; "
          "West South Central 267: Arkansas 21, Louisiana 31, Oklahoma 29, Texas 186; "
          "Mountain 13: Montana 1, Idaho 1, Wyoming 1, Colorado 4, New Mexico 2, Arizona 3, Utah 1; "
          "Pacific 82: Washington 6, Oregon 4, California 72",
    1965: "11 | 61 | New England 1: Massachusetts 1; Middle Atlantic 4: NY_UP 1, New Jersey 3; East North Central 5: Illinois 4, Michigan 1; "
          "West North Central 10: Minnesota 1, Iowa 3, Missouri 1, Nebraska 4, Kansas 1; South Atlantic 3: Maryland 1, South Carolina 1, Georgia 1; "
          "East South Central 2: Tennessee 1, Mississippi 1; West South Central 24: Arkansas 2, Louisiana 1, Oklahoma 2, Texas 19; "
          "Mountain 3: Colorado 1, Arizona 2; Pacific 9: Washington 3, Oregon 1, California 5",
    1966: "8 | 106 | Middle Atlantic 1: Pennsylvania 1; East North Central 7: Ohio 2, Indiana 2, Illinois 2, Michigan 1; West North Central 1: Minnesota 1; "
          "South Atlantic 4: West Virginia 2, Georgia 1, Florida 1; East South Central 4: Alabama 1, Mississippi 3; "
          "West South Central 75: Louisiana 1, Oklahoma 1, Texas 73; Pacific 14: Washington 5, California 9",
    1967: "8 | 40 | Middle Atlantic 5: NY_CITY 1, NY_UP 1, Pennsylvania 3; East North Central 7: Indiana 3, Illinois 1, Michigan 3; "
          "West North Central 4: Iowa 1, Missouri 1, Kansas 2; South Atlantic 2: Maryland 1, North Carolina 1; East South Central 2: Mississippi 2; "
          "West South Central 14: Arkansas 1, Louisiana 1, Oklahoma 2, Texas 10; Mountain 1: Colorado 1; Pacific 5: California 5*",
    1968: "8 | 53 | New England 2: Maine 1, Massachusetts 1; Middle Atlantic 2: NY_CITY 1, NY_UP 1; East North Central 11: Ohio 2, Indiana 3, Illinois 3, Michigan 3; "
          "West North Central 3: Iowa 1, Missouri 2; South Atlantic 3: District of Columbia 1, West Virginia 1, North Carolina 1; East South Central 1: Kentucky 1; "
          "West South Central 24: Arkansas 1, Oklahoma 1, Texas 22; Mountain 4: New Mexico 3*, Arizona 1; Pacific 3: Washington 1, California 2**",
    1969: "8 | 18 | New England 2: Maine 1, Connecticut 1; Middle Atlantic 2: NY_UP 1, Pennsylvania 1; East North Central 2: Illinois 1, Michigan 1; "
          "West North Central 1: Kansas 1; South Atlantic 1: Florida 1; East South Central 1: Alabama 1; West South Central 7: Arkansas 1, Texas 6; "
          "Mountain 1: Montana 1; Pacific 1: California 1",
    1970: "8 | 31 | East North Central 3: Illinois 1, Michigan 2; West North Central 1: Missouri 1; East South Central 1: Mississippi 1; "
          "West South Central 22: Texas 22; Mountain 1: Colorado 1; Pacific 3: Washington 1, California 2",
    1971: "8 | 17 | Middle Atlantic 1: New Jersey 1; East North Central 2: Indiana 1, Illinois 1; West North Central 1: Iowa 1; "
          "West South Central 4: Texas 4; Mountain 3: Montana 1, Colorado 1, Nevada 1; Pacific 6: Washington 1, Oregon 1, California 4",
    1972: "8 | 29 | New England 12: Maine 1, Connecticut 11; Middle Atlantic 5: NY_UP 4, NY_CITY 1; East North Central 3: Indiana 1, Michigan 1, Wisconsin 1; "
          "West North Central 1: Iowa 1; South Atlantic 2: Virginia 1, Florida 1; West South Central 4: Texas 4; Pacific 2: California 2",
    1973: "12 | 7 | Middle Atlantic 1: Pennsylvania 1; West North Central 1: Iowa 1; South Atlantic 2: Maryland 1, Virginia 1; Pacific 3: California 2, Hawaii 1",
    1974: "12 | 7 | East North Central 3: Indiana 1, Michigan 2; West North Central 2: Iowa 2; South Atlantic 1: Virginia 1; East South Central 1: Alabama 1",
    1975: "12 | 8 | New England 1: Connecticut 1; Middle Atlantic 1: Pennsylvania 1; East North Central 1: Indiana 1; East South Central 1: Tennessee 1; "
          "West South Central 2: Texas 2; Pacific 2: California 2",
    1976: "13 | 12 | New England 2: New Hampshire 1, Connecticut 1; Middle Atlantic 1: NY_CITY 1; East North Central 2: Indiana 1, Michigan 1; "
          "West North Central 1: Minnesota 1; South Atlantic 1: Maryland 1; West South Central 1: Arkansas 1; Mountain 1: Arizona 1; Pacific 3: Washington 1, California 2",
    1977: "14 | 17 | New England 2: New Hampshire 2; Middle Atlantic 1: NY_CITY 1; East North Central 1: Indiana 1; West North Central 5: Minnesota 4, North Dakota 1; "
          "South Atlantic 2: Maryland 1, South Carolina 1; West South Central 3: Texas 3; Mountain 1: Arizona 1; Pacific 2: Washington 1, Oregon 1",
    1978: "21 | 9 | East North Central 2: Ohio 1, Michigan 1; South Atlantic 3: Virginia 1, North Carolina 1, Georgia 1; Mountain 1: New Mexico 1; "
          "Pacific 3: Washington 1, California 1, Hawaii 1",
    1979: "13 | 26 | New England 1: Massachusetts 1; Middle Atlantic 9: NY_CITY 1, Pennsylvania 8; East North Central 4: Illinois 1, Wisconsin 3; "
          "West North Central 6: Minnesota 1, Iowa 3, Missouri 1, Nebraska 1; South Atlantic 1: North Carolina 1; Mountain 1: Arizona 1; Pacific 4: Washington 1, California 3",
    1980: "19 | 8 | Middle Atlantic 1: New Jersey 1; East North Central 1: Michigan 1; West South Central 1: Louisiana 1; Mountain 1: Wyoming 1; "
          "Pacific 4: Washington 1, Oregon 1, California 2",
    1981: "22 | 6 | West North Central 3: Minnesota 1, Missouri 1, Nebraska 1; South Atlantic 2: Maryland 1, West Virginia 1; Pacific 1: Washington 1",
    1982: "16 | 8 | Middle Atlantic 1: NY_CITY 1; East North Central 2: Indiana 2; West North Central 1: Iowa 1; Mountain 1: Idaho 1; Pacific 3: Washington 1, California 2",
    1983: "21 | 15 | Middle Atlantic 2: NY_CITY 1, Pennsylvania 1; East North Central 5: Ohio 1, Indiana 3, Illinois 1; West North Central 2: Missouri 2; "
          "East South Central 1: Kentucky 1; West South Central 2: Louisiana 1, Texas 1; Pacific 3: Washington 1, Oregon 1, California 1",
    1984: "16 | 8† | Middle Atlantic 2: Pennsylvania 2; West North Central 1: Minnesota 1; South Atlantic 1: Maryland 1; East South Central 1: Tennessee 1; "
          "West South Central 2: Louisiana 1, Texas 1; Pacific 1: California 1",
    1985: "12 | 7† | New England 1: Massachusetts 1; Middle Atlantic 1: NY_CITY 1; West North Central 1: Missouri 1; South Atlantic 1: Florida 1; "
          "Mountain 1: Nevada 1; Pacific 2: California 2",
    1986: "12 | 3† | East North Central 1: Michigan 1; South Atlantic 1: Florida 1; Pacific 1: California 1§",
    1987: "12 | -† | ",
    1988: "15 | 9† | New England 1: Massachusetts 1; East North Central 2: Illinois 1, Wisconsin 1; West North Central 1: Missouri 1; South Atlantic 1: South Carolina 1; "
          "West South Central 2: Oklahoma 1, Texas 1; Mountain 1: Wyoming 1; Pacific 1: Washington 1",
    1989: "13 | 5† | South Atlantic 3: Maryland 1, North Carolina 1, Georgia 1; East South Central 1: Kentucky 1; Pacific 1: California 1",
    1990: "19 | 7† | Middle Atlantic 3: NY_UP 2, Pennsylvania 1; South Atlantic 1: Florida 1; West South Central 2: Texas 2; Mountain 1: Arizona 1",
    1992: "23 | 4† | New England 1: Rhode Island 1; East South Central 1: Kentucky 1; Pacific 2: Washington 1, California 1",
}
# Symbol legends read from the page image where the OCR layer garbled them.
_NN_OLD = "Report of disease not required by State Health Department"
_M5657 = {"-": "No cases reported (1 dash)", "*": "Disease stated not notifiable (1 asterisk)",
          "**": "No report made by State (2 asterisks)", "---": "Data not available (3 dashes)"}
SCAN_IMAGE_MARKS = {
    1956: {k: (v, 3) for k, v in _M5657.items()},
    1957: {k: (v, 2) for k, v in _M5657.items()},
    1958: {"-": ("Quantity zero", 3), "*": ("Disease stated not notifiable", 3),
           "**": ("No report made by State", 3), "---": ("Data not available", 3)},
    1959: {"---": ("Data not available", 3), "-": ("Quantity zero", 3),
           "*": ("Disease stated not notifiable", 3)},
    1960: {"...": ("Data not available", 2), "-": ("Quantity zero", 2)},
    1961: {"...": ("Data not available", 2), "-": ("Quantity zero", 2)},
    1962: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1963: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1964: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1965: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1966: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1967: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1968: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1969: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1970: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1971: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1972: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1973: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1974: {"...": ("Data not available", 2), "-": ("Quantity zero", 2), "NN": (_NN_OLD, 2)},
    1975: {"NA": ("Data not available", 2), "-": ("Quantity zero", 2),
           "NN": (_NN_OLD + " (Not Notifiable)", 2)},
    1976: {"NA": ("Data not available", 2), "-": ("Quantity zero", 2),
           "NN": (_NN_OLD + " (not notifiable)", 2)},
    1977: {"NA": ("Data not available", 2), "-": ("No reported cases", 2),
           "NN": (_NN_OLD + " (not notifiable)", 2)},
    1978: {"NA": ("Data not available", 10), "-": ("No reported cases", 10),
           "NN": (_NN_OLD + " (not notifiable)", 10)},
    1979: {"NA": ("Data not available", 7), "-": ("No reported cases", 7),
           "NN": (_NN_OLD + " (not notifiable)", 7)},
    1980: {"-": ("No reported cases", 12), "NA": ("Data not available", 12),
           "NN": ("Report of disease not required by state health department (not notifiable)", 12)},
    1981: {"-": ("No reported cases", 15), "NA": ("Data not available", 15),
           "NN": ("Report of disease not required by state health department (not notifiable)", 15)},
    1985: {"-": ("No reported cases", 6), "NA": ("Data not available", 6)},
    1986: {"-": ("No reported cases", 6), "NA": ("Data not available", 6)},
    1988: {"-": ("No reported cases", 7), "NA": ("Data not available", 7)},
    1989: {"-": ("No reported cases", 6), "NA": ("Data not available", 6)},
}
# OCR spellings of area labels seen in the scans (labels only, never numbers)
SCAN_LABEL_ALIASES = {"rl": "Rhode Island", "iii": "Illinois", "lll": "Illinois",
                      "ili": "Illinois", "lii": "Illinois", "iil": "Illinois",
                      "nm": "New Mexico"}     # "N. M." in the 1978 summary
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


# (year, disease) -> (PDF page, header as printed, United States cell as printed)
SCAN_IMAGE_COLUMNS = {}
for _y, _spec in _PP_COLUMNS.items():
    _pg, _us, _rest = [x.strip() for x in _spec.split("|")]
    _vals = {US: _us}
    for _part in filter(None, (x.strip() for x in _rest.split(";"))):
        _head, _states = _part.split(":")
        _dv, _dt = _head.strip().rsplit(" ", 1)
        _vals[_dv] = _dt
        for _it in _states.split(","):
            _a, _v = _it.strip().rsplit(" ", 1)
            _vals[{"NY_UP": NY_UP, "NY_CITY": NY_CITY}.get(_a, _a)] = _v
    _ny = ["New York"] if "New York" in _vals else [NY_UP, NY_CITY]
    for _a in [US] + list(DIVISIONS) + [x for x in STATES if x != "New York"] + _ny:
        assert _a == US or _a in DIVISIONS or _a in STATES or _a in (NY_UP, NY_CITY), _a
        SCAN_IMAGE_CELLS[(_y, "polio_paralytic", _a)] = (_vals.pop(_a, "-"), int(_pg))
    assert not _vals, (_y, _vals)      # every name in the list above was a real row
    SCAN_IMAGE_COLUMNS[(_y, "polio_paralytic")] = (int(_pg), "POLIOMYELITIS Paralytic", _us)


def scan_url(year):
    r = SCAN_ISSUES[year]
    return "https://stacks.cdc.gov/view/cdc/%d/cdc_%d_DS1.pdf" % (r, r)


def scan_file(year):
    return "stacks_%d_DS1.pdf" % SCAN_ISSUES[year]


def scan_area(label):
    k = _key(label)
    if k == "newyork":          # the 1950s and early 1960s tables print one New York row
        return "New York"
    return AREA_KEYS.get(k) or SCAN_LABEL_ALIASES.get(k)


def scan_layout(year, cells, disease):
    """(need, divisions) for one scanned disease-year.
    New York is one row in the older tables and two rows (upstate, city) later.
    Alaska and Hawaii are not in the tables before they became states (1959)."""
    # a "New York" label with no number is a footnote line ("... New York)."), not a row
    single_ny = any(a == "New York" and r.strip() for (a, _, d, r, _) in cells if d == disease) or \
        any(k[0] == year and k[1] == disease and k[2] == "New York" for k in SCAN_IMAGE_CELLS)
    ny = ["New York"] if single_ny else [NY_UP, NY_CITY]
    # Alaska joins the tables in 1959, Hawaii in 1960 (statehood 1959)
    absent = {"Alaska"} if year <= 1958 else set()
    if year <= 1959:
        absent.add("Hawaii")
    if year > 1959:
        absent = set()
    if year <= 1958:
        absent = {"Alaska", "Hawaii"}
    divs = {}
    for div, members in DIVISIONS.items():
        m = []
        for s in members:
            if s in (NY_UP, NY_CITY):
                if s == NY_UP:
                    m.extend(ny)
                continue
            if s in absent:
                continue
            m.append(s)
        divs[div] = m
    states = [s for v in divs.values() for s in v]
    return states + [US] + list(divs), divs


NOT_YET_STATE = "not in the table (not yet a state)"


def scan_hepatitis_a_column(texts):
    """{"hepatitis_a": column index} for a scanned table page, or {}.
    The column is headed "Hepatitis, infectious" (1966-1971), "Infectious (A)"
    (1972), a bare "A" under "Hepatitis" (1973-1977) or "Hepatitis A". Serum,
    B, non-A non-B and unspecified hepatitis, post-infectious encephalitis and
    the by-month and by-age detail tables are not this column."""
    for i, t in enumerate(texts):
        low = re.sub(r"\s+", " ", t.lower())
        sq = re.sub(r"[^a-z]", "", low)
        if sq == "a":
            return {"hepatitis_a": i}
        if "hepatitis" not in sq and "infectious" not in sq:
            continue
        if re.search(r"serum|unsp|nona|hepatitisb|post", sq) or re.search(r"jan|apr|<1|\b5-9\b", low):
            continue
        if "infectious" in sq or re.search(r"hepatitisa($|[^n])", sq):
            return {"hepatitis_a": i}
    return {}


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
        fix0 = SCAN_PAGE_FIXES.get((year, pno), {})
        if fix0.get("image_only"):
            # the OCR layer of this page cannot be used at all: every cell of
            # these columns comes from SCAN_IMAGE_CELLS
            for d, (hdr_txt, us_txt) in fix0["image_only"].items():
                if d not in seen:
                    seen[d] = pno
                    res["colmap"].append((d, pno, hdr_txt + " [read from page image]", us_txt))
            continue
        # spaces removed: some OCR layers are letter-spaced ("M U M P S")
        squeezed = re.sub(r"\s", "", text)
        if not re.search(r"(?i)pertussis|indigenous|rubeola|measles|mumps|hepatitis", squeezed):
            continue
        # a page that only mentions hepatitis is read for hepatitis A alone: its
        # other headers ("Imported" under Malaria) are not the measles columns
        hepatitis_page_only = not re.search(r"(?i)pertussis|indigenous|rubeola|measles|mumps", squeezed)
        if len(re.findall(r"\d", text)) < 250:
            continue
        slope, lines = deskewed_lines(page)
        us_idx = None
        n_lab = 0
        for li, line in enumerate(lines):
            # label = the words before the first number ("U N IT E D  S T A T E S ....")
            k = next((i for i, w in enumerate(line) if re.search(r"\d", w[4])), len(line))
            if k >= 1 and len(line) - k >= 2 and _key("".join(w[4] for w in line[:k])) == "unitedstates" \
                    and sum(1 for w in line[k:] if re.search(r"\d", w[4])) >= (len(line) - k) * 0.7:
                us_idx, n_lab = li, k
                break
        if us_idx is None:
            continue
        us_vals = merge_close(lines[us_idx][n_lab:])
        us_vals = [w for w in us_vals if re.search(r"\d", w[4])]
        fix = SCAN_PAGE_FIXES.get((year, pno), {})
        for (x0, x1, txt) in fix.get("insert_us", []):
            # a US total the OCR layer dropped, read from the page image
            us_vals.append((x0, us_vals[0][1], x1, us_vals[0][3], txt))
        us_vals.sort(key=lambda w: w[0])
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
        if len(rows) < fix.get("min_rows", 45):
            continue
        us_y = (lines[us_idx][0][1] + lines[us_idx][0][3]) / 2 - slope * lines[us_idx][0][0]
        hdr = []
        for line in lines:
            ly = (line[0][1] + line[0][3]) / 2 - slope * line[0][0]
            s_ = " ".join(w[4] for w in line)
            if re.search(r"(?i)reported cases|MMWR|United States[,.]|SUMMARY TABLES|continued", s_):
                continue
            if us_y - 70 < ly < us_y - 2.5:
                # "Im" "ported" -> "Imported"; "M U M P S" (letter-spaced OCR) -> "MUMPS"
                hdr.extend(merge_close(line, gap=2.6))
        texts = [[] for _ in range(ncol)]
        for w in sorted(hdr, key=lambda w: (round(w[1]), w[0])):
            if w[4] == "Area":
                continue
            c = (w[0] + w[2]) / 2
            j = min(range(ncol), key=lambda j: abs(c - centers[j]))
            texts[j].append(w[4])
        texts = [" ".join(t) for t in texts]
        if fix.get("only_these_headers"):
            texts = ["" for _ in texts]
        for j, txt in fix.get("headers", {}).items():
            # column header the OCR layer lost, read from the page image
            texts[j] = txt + " [header read from page image]"
        try:
            cmap = {} if hepatitis_page_only else classify_columns(texts, False)
            if re.search(r"(?i)post-?infectious|arbovirus", " ".join(texts)) or (year == 1964 and pno == 9):
                # the encephalitis table has "Measles" and "Mumps" columns of its own
                # (post-infectious encephalitis): never the disease counts
                cmap = {}
            cmap.update(scan_hepatitis_a_column(texts))
        except ValueError as e:
            res["warn"].append("p%d: %s" % (pno, e))
            continue
        cmap = {d: j for d, j in cmap.items() if d in SCAN_DISEASES and d not in seen
                and (year, d) not in SCAN_IMAGE_COLUMNS}
        if not cmap:
            continue
        for (area, lab, cols) in rows:
            for d, j in cmap.items():
                raw = "".join(w[4] for w in sorted(cols.get(j, []), key=lambda w: w[0]))
                raw = raw.replace("_", "-")
                res["cells"].append((area, lab, d, raw,
                                     "Table by geographic division and area, PDF page %d, column \"%s\""
                                     % (pno, texts[j])))
        last_y = max(max(w[3] for ws in cols.values() for w in ws) if cols else 0
                     for (_, _, cols) in rows)
        for d, j in cmap.items():
            seen[d] = pno
            res["colmap"].append((d, pno, texts[j], us_vals[j][4]))
            # where the column sits on the page, for rendering it as an image
            res.setdefault("geom", {})[d] = (pno, lower[j], upper[j], lower[0], us_y - 40, last_y + 4)
    for (y_, d), (pg, hdr_txt, us_txt) in SCAN_IMAGE_COLUMNS.items():
        # a whole column read from the page image (every cell is in SCAN_IMAGE_CELLS)
        if y_ == year and d not in seen:
            seen[d] = pg
            res["colmap"].append((d, pg, hdr_txt + " [read from page image]", us_txt))
    res["marks"] = find_mark_defs(res["text"])
    for mk, (meaning, pg) in SCAN_IMAGE_MARKS.get(year, {}).items():
        # the legend as seen on the page image replaces whatever the OCR layer gave
        res["marks"][mk] = "%s (p.%d; legend read from the page image)" % (meaning, pg)
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


def scan_validate(cells, marks, disease, year=None, all_errors=False):
    """Strict acceptance test for one disease of one scanned year.
    Returns (ok, reason, {area: (cases, flag)}). Any state cell that the OCR
    layer did not read as a number or a mark fails the disease-year.
    Cells listed in SCAN_IMAGE_CELLS replace the OCR text and carry the flag
    'read from page image'. With all_errors=True every failing division is
    listed (used to decide which cells to look at on the image)."""
    need, divisions = scan_layout(year, cells, disease)
    got = {}
    unread = []

    def interpret(text, prefix):
        """-> (cases, flag) or None when the text is not a number or a defined mark."""
        text = text.strip()
        # a footnote mark printed in front of the number ("*873") goes behind it
        text = re.sub(r"^([%s]+)(\d.*)$" % FOOT, r"\2\1", text)
        if re.fullmatch(r"[.…·]{3,}", text):     # "..." = data not available (1960-1974)
            return ("", prefix + "...") if "..." in marks else None
        if "---" in marks:
            # 1956-1959: one dash = zero, three dashes = data not available. The
            # OCR layer cannot be trusted to keep the count, so a dash is only
            # accepted when read from the page image.
            if re.fullmatch(r"[%s]+" % DASHES, text):
                if not prefix:
                    return None
                return ("", prefix + "---") if text == "---" else \
                    ((0, prefix + "-") if text == "-" else None)
        if text in ("*", "**"):                   # 1956-1959: not notifiable / no report
            return ("", prefix + text) if text in marks else None
        num, mark, sym = parse_cell(text)
        if num is not None:
            if prefix:     # keep a printed footnote mark, e.g. "read from page image; *"
                return (num, prefix.rstrip(": ") + ("; " + sym if sym else ""))
            return (num, sym)
        if mark == "-" and dash_is_zero(marks):
            return (0, prefix + "-" + ("" if prefix else sym))
        # NR is printed once (North Carolina, 1974) and the issue does not define
        # it; it is kept as a mark with no number, never as zero
        if mark in ("NN", "NA", "N", "U", "NR") or (mark in marks and mark != "-"):
            return ("", prefix + mark)
        return None

    for (area, label, d, raw, table) in cells:
        if d != disease or area not in need:
            continue
        img = SCAN_IMAGE_CELLS.get((year, disease, area))
        if img is not None:
            ed = SCAN_EDITOR_READINGS.get((year, disease, area))
            rec = interpret(img[0], f"read from page image, {ed}: " if ed else "read from page image: ")
            if rec is None:
                return False, "image reading not usable: %s = %r" % (area, img[0]), got
            got[area] = rec
            continue
        rec = interpret(raw, "")
        if rec is None:
            unread.append("%s=%r" % (area, raw))
            got[area] = ("", "unread")
        else:
            got[area] = rec
    # rows whose label the OCR layer lost entirely, read from the image
    for (y_, d_, area), (txt, pg) in SCAN_IMAGE_CELLS.items():
        if y_ == year and d_ == disease and area not in got:
            rec = interpret(txt, "read from page image: ")
            if rec is None:
                return False, "image reading not usable: %s = %r" % (area, txt), got
            got[area] = rec
    errors = []
    if unread:
        errors.append("%d cells not readable in the OCR layer: %s" % (len(unread), ", ".join(unread)))
    miss = [a for a in need if a not in got]
    if miss:
        errors.append("%d rows not found: %s" % (len(miss), ", ".join(miss)))
    if errors and not all_errors:
        return False, errors[0], got
    n = lambda a: got[a][0] if a in got and got[a][0] != "" else 0
    for div, members in divisions.items():
        if div not in got or got[div][0] == "" or sum(n(m) for m in members) != got[div][0]:
            errors.append("%s: states add to %d, printed %s" % (
                div, sum(n(m) for m in members), got.get(div, ("missing",))[0]))
    if US not in got or got[US][0] == "":
        errors.append("US total not a number")
    elif sum(n(d_) for d_ in divisions) != got[US][0]:
        errors.append("divisions add to %d, printed US total %d" % (
            sum(n(d_) for d_ in divisions), got[US][0]))
    if errors:
        return False, " | ".join(errors) if all_errors else errors[0], got
    for s in ("Alaska", "Hawaii"):
        if s not in need and s not in got:
            got[s] = ("", NOT_YET_STATE)
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
    # "No reported cases" (1977 on) or "Quantity zero" (1968-1976 legends)
    return bool(re.search(r"(?i)no reported cases|no cases reported|quantity zero", d))


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
        img = "read from page image"
        if img in f1 or img in f2:
            parts = [("upstate" if img in f1 else ""), ("NYC" if img in f2 else "")]
            return c1 + c2, "%s (%s part)" % (img, " and ".join(p for p in parts if p))
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


def got_ny_flag(got):
    """Flag of the combined New York row for one disease ('' if numeric or absent)."""
    if NY_UP in got and NY_CITY in got and "New York" not in got:
        return combine_ny(got[NY_UP], got[NY_CITY])[1]
    return ""


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
    imgrows = []

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
            result = "OK" if ok else "CHECK"
            # New York row left blank because one part is not a number (upstate
            # NN in 1968-1973): the US total still contains the other part
            ny_part = re.search(r"other part=(\d+)", got_ny_flag(got))
            if not ok and usrec[0] != "" and not missing and ny_part and \
                    usrec[0] - total == int(ny_part.group(1)):
                result = ("OK (difference = New York City cases; the New York row is blank "
                          "because upstate New York is marked NN)")
            sumcheck.append([year, d, total, usrec[0], usrec[1],
                             "" if usrec[0] == "" else usrec[0] - total,
                             result, ";".join(missing), ";".join(marks_seen), fname])
        if zero_note:
            for d, sentence in zero_note.items():
                if d in by:
                    continue
                for st in STATES:
                    out_rows.append([year, st, d, 0, "fn0", url, fname,
                                     'Table 2 footnote: "%s"' % sentence[:300]])
                sumcheck.append([year, d, 0, 0, "fn0", 0, "OK (footnote: no cases in US)", "", "", fname])

    # ---- scanned annual summaries (measles, pertussis, mumps and hepatitis A)
    for year in sorted(SCAN_ISSUES):
        sc = parse_scan_pdf(year)
        if sc is None:
            problems.append("%d: scan not downloaded" % year)
            scanrows.append([year, "", "no", "file not downloaded", "", "", ""])
            continue
        heads = {d: (pno, text, usval) for (d, pno, text, usval) in sc["colmap"]}
        results = {}
        # before 1968 (mumps not yet notifiable) only pertussis is read
        wanted = ("pertussis",) if year < 1968 else \
            ("measles", "measles_indigenous", "measles_imported", "pertussis", "mumps")
        if year >= 1966:     # the first year infectious hepatitis has its own column
            wanted += ("hepatitis_a",)
        if year <= 1967:     # measles from the first scanned year (Tycho has no New York row for 1964-1967)
            wanted += ("measles",)
        wanted += ("polio_paralytic",)     # every scanned year, 1956-1992
        heads = {d: v for d, v in heads.items() if d in wanted}
        for d in wanted:
            if d not in heads:
                continue
            results[d] = scan_validate(sc["cells"], sc["marks"], d, year)
        split = "measles_indigenous" in heads or "measles_imported" in heads
        accept = set()
        for d in ("pertussis", "mumps", "hepatitis_a", "polio_paralytic"):
            if d in results and results[d][0]:
                accept.add(d)
        if split:
            if all(d in results and results[d][0] for d in ("measles_indigenous", "measles_imported")):
                accept.update(["measles_indigenous", "measles_imported"])
        elif "measles" in results and results["measles"][0]:
            accept.add("measles")
        for d in wanted:
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
        ocr = {}
        for (area, label, d, raw, table) in sc["cells"]:
            ocr.setdefault((d, area), (label, raw))
            tab.setdefault(d, table + " (scan, OCR text layer)")
        for (d, pno, text, usval) in sc["colmap"]:
            tab.setdefault(d, "Table by geographic division and area, PDF page %d, column \"%s\" "
                              "(scan, OCR text layer)" % (pno, text))
        for d in sorted(accept):
            for area, rec in results[d][2].items():
                label, raw = ocr.get((d, area), ("(not in the table)" if rec[1] == NOT_YET_STATE
                                                 else "(label not legible in the OCR layer)", ""))
                by[d][area] = rec
                area_rows.append([year, area, label, d, rec[0], rec[1], raw,
                                  sc["url"], sc["file"], tab[d]])
                if rec[1].startswith("read from page image"):
                    img = SCAN_IMAGE_CELLS[(year, d, area)]
                    imgrows.append([year, d, area, img[1], raw, img[0], sc["file"]])
            if any(SCAN_IMAGE_CELLS.get((year, d, a)) for a in results[d][2]):
                tab[d] = tab[d].replace("(scan, OCR text layer)",
                                        "(scan, OCR text layer; cells flagged 'read from page image' "
                                        "were read from the rendered page)")
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
    write("checks_image_cells.csv",
          ["year", "disease", "area", "pdf_page", "ocr_text_layer_had", "read_from_page_image",
           "source_file"], imgrows)
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
