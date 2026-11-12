"""Charts for the essay "Public Health Is Losing a Measles Argument It Should Be Winning" (slug measles-public-data-warning).

  01  Utah: kindergarten MMR coverage by school year against 95%, with Utah's measles cases each year under it
  02  Six states, county measles cases in 2025 and in 2026, on county kindergarten MMR coverage
  03  U.S. measles cases each year, 1920 to 2026, log scale, with the vaccine licensing years marked
  social: 02 as a GIF (each state flips from 2025 to 2026) and the national split-tile map, 2015 to 2026, as a GIF

Every number comes from viz/data.json (the map's own data) and data/county_measles.csv. Static charts use the dark
palette (background #181A1B, text #BBBDC0). Pages are drawn as SVG in HTML and screenshotted with headless Chrome.
"""
import datetime as dt
import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "viz" / "data.json").read_text())
POST = ROOT / "posts" / "measles-public-data-warning"
IMG, SOC = POST / "images", POST / "social"
TMP = POST / ".frames"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PIL_PY = Path.home() / ".claude" / "tools" / "prismic" / ".venv" / "bin" / "python"   # carries Pillow, for the GIFs

BG, INK, INK2, INK3, GRID = "#181A1B", "#EDEEEF", "#BBBDC0", "#8a8c8f", "#2f3234"
GREEN, AMBER, RED, NOFIG, DOT = "#86c383", "#f4c457", "#e2675f", "#2b2e30", "#b0182f"
SANS, SERIF = "Helvetica Neue,Helvetica,Arial,sans-serif", "Georgia,serif"
Y0, Y1 = D["y0"], D["y1"]
STATES = {s["k"]: s for s in D["states"]}
cov_fill = lambda v: NOFIG if v is None else GREEN if v >= 95 else AMBER if v >= 90 else RED
rate_fill = lambda r: NOFIG if r is None else RED if r > 1 else AMBER if r >= 0.1 else GREEN
fmt = lambda n: f"{n:,}"


def wash(hexc, k=0.42):
    """a color mixed toward the background, so the county shading sits behind the case circles"""
    a = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(BG[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * k + y * (1 - k)):02x}" for x, y in zip(a, b))


WGREEN, WAMBER, WRED = wash(GREEN), wash(AMBER), wash(RED)
county_fill = lambda v: NOFIG if v is None else WGREEN if v >= 95 else WAMBER if v >= 90 else WRED


def mmwr_end(year, week):
    """the Saturday that ends MMWR week `week` of `year` (week 1 = first Sunday-to-Saturday week with 4+ days in the year)"""
    j1 = dt.date(year, 1, 1)
    dow = (j1.weekday() + 1) % 7   # Sunday = 0
    start = j1 - dt.timedelta(days=dow) if dow <= 3 else j1 + dt.timedelta(days=7 - dow)
    return start + dt.timedelta(days=week * 7 - 1)


THROUGH = mmwr_end(D["partial"]["year"], D["partial"]["week"])
THROUGH_TXT = f"{THROUGH:%B} {THROUGH.day}"
CM_THROUGH = dt.date.fromisoformat(D["cmeaslesThrough"])
CM_TXT = f"{CM_THROUGH:%B} {CM_THROUGH.day}"
CREDIT = "Data 4 The People."


def shoot(svg, w, h, out):
    html = TMP / (out.stem + ".html")
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:{BG}}}</style></head><body>{svg}</body></html>')
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    f"--screenshot={out}", html.as_uri()], check=True, capture_output=True)


def foot(x, y, text, w, size=18):
    """the source line, wrapped so it never runs off the image (about 0.5 em a character)"""
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > (w - 2 * x) / (size * 0.5):
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    return "".join(f'<text x="{x}" y="{y - (len(lines) - 1 - i) * (size + 6)}" font-size="{size}" fill="{INK3}">{l}</text>' for i, l in enumerate(lines))


def svg_open(w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{SANS}"><rect width="{w}" height="{h}" fill="{BG}"/>'


def title(x, y, t, sub=None, size=40):
    out = f'<text x="{x}" y="{y}" font-size="{size}" font-weight="700" fill="{INK}" font-family="{SERIF}">{t}</text>'
    if sub:
        out += f'<text x="{x}" y="{y + 40}" font-size="22" fill="{INK2}">{sub}</text>'
    return out


# ---------- 01 Utah ----------
def chart_utah():
    W, H = 1600, 1020
    k = D["vax"]["kinder"]["mmr"]["UT"]
    ys = list(range(2010, Y1 + 1))
    cov = {y: k[str(y)][0] for y in ys if str(y) in k}
    cases = {y: D["cases"]["measles"]["UT"][y - Y0] for y in ys}
    ml, mr = 140, 80
    X = lambda y: ml + (y - ys[0] + 0.5) / len(ys) * (W - ml - mr)
    top0, top1, lo, hi = 220, 640, 85, 100
    Yc = lambda v: top1 - (v - lo) / (hi - lo) * (top1 - top0)
    g = svg_open(W, H)
    g += title(80, 88, "Utah fell below 95% a decade before its measles outbreak",
               f"Utah kindergartners with the measles vaccine (MMR) each school year, and measles cases each year, 2010 to {Y1}")
    for v in (85, 90, 95, 100):
        g += f'<line x1="{ml}" x2="{W - mr}" y1="{Yc(v)}" y2="{Yc(v)}" stroke="{GRID}"/><text x="{ml - 14}" y="{Yc(v) + 7}" font-size="20" fill="{INK3}" text-anchor="end">{v}%</text>'
    g += f'<line x1="{ml}" x2="{W - mr}" y1="{Yc(95)}" y2="{Yc(95)}" stroke="{INK2}" stroke-width="2" stroke-dasharray="8 6"/>'
    g += f'<text x="{W - mr}" y="{Yc(95) - 12}" font-size="20" fill="{INK2}" text-anchor="end">95%: the national target</text>'
    # the line, cut where a school year has no figure (none for 2010-11)
    path, prev = "", None
    for y in ys:
        if y not in cov:
            prev = None
            continue
        path += ("L" if prev is not None else "M") + f"{X(y):.1f},{Yc(cov[y]):.1f}"
        prev = y
    g += f'<path d="{path}" fill="none" stroke="{INK2}" stroke-width="3"/>'
    for y, v in cov.items():
        g += f'<circle cx="{X(y)}" cy="{Yc(v)}" r="9" fill="{cov_fill(v)}" stroke="{BG}" stroke-width="2"/>'
    for y, below in ((2014, False), (2015, True), (Y1, False)):   # the last year above 95%, the first below, and the latest
        g += f'<text x="{X(y)}" y="{Yc(cov[y]) + (38 if below else -20)}" font-size="21" font-weight="700" fill="{INK}" text-anchor="middle">{cov[y]:.1f}%</text>'
    g += f'<text x="{ml}" y="{top0 - 22}" font-size="21" font-weight="700" fill="{INK2}">Kindergartners with the measles vaccine (dots: <tspan fill="{GREEN}">95% or more</tspan>, <tspan fill="{AMBER}">90% to under 95%</tspan>, <tspan fill="{RED}">under 90%</tspan>)</text>'
    # cases
    b0, b1 = 720, 900
    cmax = max(cases.values())
    Yb = lambda n: b1 - n / cmax * (b1 - b0 - 30)
    g += f'<text x="{ml}" y="{b0 - 14}" font-size="21" font-weight="700" fill="{INK2}">Measles cases reported in Utah</text>'
    g += f'<line x1="{ml}" x2="{W - mr}" y1="{b1}" y2="{b1}" stroke="{GRID}"/>'
    bw = (W - ml - mr) / len(ys) * 0.6
    for y in ys:
        n = cases[y]
        if n:
            g += f'<rect x="{X(y) - bw / 2}" y="{Yb(n)}" width="{bw}" height="{b1 - Yb(n)}" fill="{RED if y >= 2025 else INK3}" opacity="{0.6 if y == Y1 else 1}"/>'
        g += f'<text x="{X(y)}" y="{(Yb(n) if n else b1) - 8}" font-size="19" fill="{INK if n >= 100 else INK3}" text-anchor="middle" font-weight="{700 if n >= 100 else 400}">{n}</text>'
        g += f'<text x="{X(y)}" y="{b1 + 30}" font-size="19" fill="{INK3}" text-anchor="middle">{y}</text>'
    g += foot(ml, H - 24, f"Year is the spring of the school year; no state figures for 2010-11. {Y1} cases run through {THROUGH_TXT} and are provisional (faded bar). Sources: CDC SchoolVaxView and CDC disease tables. {CREDIT}", W)
    g += "</svg>"
    shoot(g, W, H, IMG / "01-utah-decade.png")
    # the hero: the same chart drawn at 1680x1080 (scaled as vector, so the type stays sharp), on the same background
    hero = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1080" viewBox="0 0 1680 1080"><rect width="1680" height="1080" fill="{BG}"/>'
            f'<svg x="0" y="0" width="1680" height="1080" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" font-family="{SANS}">{g[g.index(">") + 1:]}</svg>')
    shoot(hero, 1680, 1080, IMG / "measles-public-data-warning-hero-1680x1080.png")
    return cov, cases


# ---------- 02 six states, county measles 2025 and 2026 ----------
cm = pd.read_csv(ROOT / "data" / "county_measles.csv", dtype={"fips": str})
cm["st_name"] = cm.location_name.str.split(", ").str[-1]
NAME_TO_ST = {s["n"]: k for k, s in STATES.items()}
cm["st"] = cm.st_name.map(NAME_TO_ST)
drawn = cm[~cm.fips.str.startswith("000")]
# Utah reports most cases by local health district, each a group of whole counties; a district's cases are drawn as
# one circle at the middle of its counties' centers (Utah's local health departments)
DISTRICTS = {
    "Bear River, Utah": ["49003", "49005", "49033"],                                   # Box Elder, Cache, Rich
    "Central, Utah": ["49023", "49027", "49031", "49039", "49041", "49055"],           # Juab, Millard, Piute, Sanpete, Sevier, Wayne
    "Southeast Health District, Utah": ["49007", "49015", "49019"],                    # Carbon, Emery, Grand
    "Southwest Health District, Utah": ["49001", "49017", "49021", "49025", "49053"],  # Beaver, Garfield, Iron, Kane, Washington
    "Tricounty, Utah": ["49009", "49013", "49047"],                                    # Daggett, Duchesne, Uintah
}
# the six states with the most cases in the last year, counted from every row (county, district or unknown)
SIX = cm[cm.year == Y1].groupby("st").cases.sum().sort_values(ascending=False).head(6).index.tolist()
YEAR_A, YEAR_B = Y1 - 1, Y1
PX_R = lambda n: 2.5 + math.sqrt(n) * 1.7   # circle radius in pixels, the same scale on every map


def county_map(st, year, w, h):
    """one state's counties colored by the latest county MMR figure up to `year`, with that year's measles circles"""
    sh = D["shapes"][st]
    bx, by, bw, bh = sh["box"]
    scale = min(w / bw, h / bh)
    vw, vh = w / scale, h / scale   # the viewBox that fits the state, centered
    vx, vy = bx - (vw - bw) / 2, by - (vh - bh) / 2
    cy = [int(y) for f in sh["c"] for y in (D["cmmr"].get(f) or {})]
    vyear = max([y for y in cy if y <= year], default=None)
    out = f'<svg x="0" y="0" width="{w}" height="{h}" viewBox="{vx} {vy} {vw} {vh}" style="overflow:visible">'
    for f, (name, d) in sh["c"].items():
        v = (D["cmmr"].get(f) or {}).get(str(vyear)) if vyear else None
        out += f'<path d="{d}" fill="{county_fill(v)}" stroke="{BG}" stroke-width="{0.6 / scale}"/>'
    out += f'<path d="{sh["d"]}" fill="none" stroke="{INK2}" stroke-width="{1.2 / scale}"/>'
    rows = cm[(cm.st == st) & (cm.year == year)].sort_values("cases", ascending=False)
    for r in rows.itertuples():
        if r.location_name in DISTRICTS:   # a district: the middle of its counties' centers
            pts = [sh["cc"][f] for f in DISTRICTS[r.location_name] if f in sh["cc"]]
            c = [sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)]
        else:
            c = sh["cc"].get(r.fips)
        if c:
            out += f'<circle cx="{c[0]}" cy="{c[1]}" r="{PX_R(r.cases) / scale}" fill="{DOT}" fill-opacity=".85" stroke="#ffffff" stroke-width="{1 / scale}"/>'
    return out + "</svg>", int(cm[(cm.st == st) & (cm.year == year)].cases.sum()), vyear


def legend_circles(x, y):
    out = f'<text x="{x}" y="{y}" font-size="20" fill="{INK2}">Measles cases in a county or district:</text>'
    cx = x + 340
    for n in (10, 100, 500):
        r = PX_R(n)
        out += f'<circle cx="{cx + r}" cy="{y - 7}" r="{r}" fill="{DOT}" fill-opacity=".85" stroke="#fff" stroke-width="1"/><text x="{cx + 2 * r + 8}" y="{y}" font-size="20" fill="{INK2}">{n}</text>'
        cx += 2 * r + 70
    out += f'<text x="{cx + 20}" y="{y}" font-size="20" fill="{INK2}">County kindergartners with 2 MMR doses: <tspan fill="{GREEN}">95% or more</tspan>  <tspan fill="{AMBER}">90% to under 95%</tspan>  <tspan fill="{RED}">under 90%</tspan>  <tspan fill="{INK3}">no figure</tspan></text>'
    return out


def chart_six():
    W, H = 1600, 1400
    mw, mh = 330, 240
    g = svg_open(W, H)
    g += title(80, 88, f"Measles cases by county, {YEAR_A} and {YEAR_B}",
               f"The six states with the most {YEAR_B} cases. {YEAR_B} runs through {CM_TXT}.")
    g += legend_circles(80, 190)
    for i, st in enumerate(SIX):
        col, row = i % 2, i // 2
        x0, y0 = 80 + col * 760, 250 + row * 355
        a, na, va = county_map(st, YEAR_A, mw, mh)
        b, nb, vb = county_map(st, YEAR_B, mw, mh)
        g += f'<text x="{x0}" y="{y0 + 22}" font-size="24" font-weight="700" fill="{INK}">{STATES[st]["n"]}</text>'
        g += f'<text x="{x0 + mw + 30}" y="{y0 + 22}" font-size="20" fill="{INK2}" text-anchor="start"></text>'
        for j, (m, n, yy) in enumerate(((a, na, YEAR_A), (b, nb, YEAR_B))):
            mx = x0 + j * (mw + 40)
            g += f'<g transform="translate({mx},{y0 + 40})">{m}</g>'
            g += f'<text x="{mx}" y="{y0 + 40 + mh + 40}" font-size="20" fill="{INK2}"><tspan font-weight="700" fill="{INK}">{yy}:</tspan> {fmt(n)} {"case" if n == 1 else "cases"}</text>'
    g += foot(80, H - 24, f"Counties are colored by the latest county figures, 2024-25. Utah reports most cases by health district, so its districts are drawn as one circle each, at the middle of their counties. Source: Johns Hopkins University. {CREDIT}", W)
    g += "</svg>"
    shoot(g, W, H, IMG / "02-six-states-2025-2026.png")


def gif_six():
    """the six states, one year at a time: 2025, then 2026"""
    W, H = 1200, 1000
    mw, mh = 360, 270
    frames = []
    for yy in (YEAR_A, YEAR_B):
        g = svg_open(W, H)
        g += f'<text x="60" y="70" font-size="34" font-weight="700" fill="{INK}" font-family="{SERIF}">Measles cases by county</text>'
        g += f'<text x="{W - 60}" y="76" font-size="64" font-weight="700" fill="{INK}" text-anchor="end">{yy}</text>'
        g += f'<text x="60" y="108" font-size="20" fill="{INK2}">The six states with the most {YEAR_B} cases{f", through {CM_TXT}" if yy == YEAR_B else ""}. Utah’s cases are drawn by health district.</text>'
        for i, st in enumerate(SIX):
            col, row = i % 3, i // 3
            x0, y0 = 60 + col * 380, 150 + row * 380
            m, n, _ = county_map(st, yy, mw, mh)
            g += f'<text x="{x0}" y="{y0 + 20}" font-size="22" font-weight="700" fill="{INK}">{STATES[st]["n"]}</text>'
            g += f'<g transform="translate({x0},{y0 + 34})">{m}</g>'
            g += f'<text x="{x0}" y="{y0 + 34 + mh + 26}" font-size="20" fill="{INK2}">{fmt(n)} {"case" if n == 1 else "cases"}</text>'
        g += f'<text x="60" y="{H - 24}" font-size="17" fill="{INK3}">Circles: confirmed cases (Johns Hopkins). Counties: kindergartners with 2 MMR doses, 2024-25 (<tspan fill="{GREEN}">95%+</tspan> <tspan fill="{AMBER}">90 to 94.9%</tspan> <tspan fill="{RED}">under 90%</tspan>). {CREDIT}</text>'
        g += "</svg>"
        p = TMP / f"six-{yy}.png"
        shoot(g, W, H, p)
        frames.append(p)
    make_gif(frames, [2600, 4000], SOC / "six-states-2025-2026.gif")


def gif_cycle():
    """one state at a time, 2025 beside 2026, three seconds each"""
    W, H = 1200, 900
    mw, mh = 520, 470
    frames = []
    for k, st in enumerate(SIX):
        g = svg_open(W, H)
        g += f'<text x="60" y="70" font-size="34" font-weight="700" fill="{INK}" font-family="{SERIF}">Measles cases by county, {YEAR_A} and {YEAR_B}</text>'
        g += f'<text x="60" y="108" font-size="20" fill="{INK2}">The six states with the most {YEAR_B} cases. {YEAR_B} runs through {CM_TXT}.</text>'
        g += f'<text x="60" y="170" font-size="40" font-weight="700" fill="{INK}">{STATES[st]["n"]}</text>'
        g += f'<text x="{W - 60}" y="170" font-size="22" fill="{INK3}" text-anchor="end">{k + 1} of {len(SIX)}</text>'
        for j, yy in enumerate((YEAR_A, YEAR_B)):
            m, n, _ = county_map(st, yy, mw, mh)
            mx = 60 + j * (mw + 40)
            g += f'<g transform="translate({mx},200)">{m}</g>'
            g += f'<text x="{mx}" y="{200 + mh + 44}" font-size="26" fill="{INK2}"><tspan font-weight="700" fill="{INK}">{yy}:</tspan> {fmt(n)} {"case" if n == 1 else "cases"}</text>'
        if st == "UT":
            g += f'<text x="60" y="{H - 104}" font-size="18" fill="{INK2}">Utah reports most cases by health district, so each district is one circle.</text>'
        g += f'<text x="60" y="{H - 66}" font-size="18" fill="{INK2}">Circles: confirmed measles cases in a county or district (Johns Hopkins).</text>'
        g += f'<text x="60" y="{H - 40}" font-size="18" fill="{INK2}">Counties: kindergartners with 2 MMR doses, 2024-25 (<tspan fill="{GREEN}">95%+</tspan> <tspan fill="{AMBER}">90 to 94.9%</tspan> <tspan fill="{RED}">under 90%</tspan>). Dark gray: no figure.</text>'
        g += f'<text x="60" y="{H - 14}" font-size="16" fill="{INK3}">{CREDIT}</text></svg>'
        p = TMP / f"cycle-{st}.png"
        shoot(g, W, H, p)
        frames.append(p)
    make_gif(frames, [3000] * len(frames), SOC / "six-states-one-at-a-time.gif")


# ---------- 03 U.S. cases, 1920 to 2026 ----------
def chart_century():
    W, H = 1600, 900
    ys = list(range(Y0, Y1 + 1))
    tot = {y: sum(D["cases"]["measles"][s][y - Y0] or 0 for s in STATES) for y in ys}
    ml, mr, t0, t1 = 130, 70, 200, 760
    top = math.ceil(math.log10(max(tot.values())))
    bw = (W - ml - mr) / len(ys)
    X = lambda y: ml + (y - Y0) * bw
    Yl = lambda n: t1 - math.log10(max(1, n)) / top * (t1 - t0)
    g = svg_open(W, H)
    g += title(80, 88, f"Measles cases in the U.S. each year, {Y0} to {Y1}",
               "Reported cases, on a log scale: each gridline is a step of 10, so both the peak and recent years show")
    for kk in range(0, top + 1):
        v = 10 ** kk
        g += f'<line x1="{ml}" x2="{W - mr}" y1="{Yl(v)}" y2="{Yl(v)}" stroke="{GRID}"/><text x="{ml - 14}" y="{Yl(v) + 7}" font-size="20" fill="{INK3}" text-anchor="end">{fmt(v)}</text>'
    for y in ys:
        n = tot[y]
        if n:
            g += f'<rect x="{X(y) + 1}" y="{Yl(n)}" width="{bw - 2}" height="{t1 - Yl(n)}" fill="{RED if y >= 2025 else INK3}" opacity="{0.6 if y == Y1 else 1}"/>'
    for y in range(1920, Y1 + 1, 20):
        g += f'<text x="{X(y) + bw / 2}" y="{t1 + 32}" font-size="20" fill="{INK3}" text-anchor="middle">{y}</text>'
    for ly, lt in sorted(D["licensed"]["mmr"]):
        if "Measles" in lt:
            g += f'<line x1="{X(ly) + bw / 2}" x2="{X(ly) + bw / 2}" y1="{t0 - 10}" y2="{t1}" stroke="{INK2}" stroke-dasharray="5 5"/><text x="{X(ly) + bw / 2 + 10}" y="{t0 + 4}" font-size="20" fill="{INK2}">{ly}: measles vaccine licensed</text>'
    peak = max(ys, key=lambda y: tot[y])
    low = min((y for y in ys if y > 1990), key=lambda y: tot[y])
    since = max(y for y in ys if y < Y1 and tot[y] >= tot[Y1])
    for y, txt, anchor in ((peak, f"{fmt(tot[peak])} in {peak}", "start"), (Y1, f"{fmt(tot[Y1])} in {Y1}, most since {since}", "end")):
        g += f'<text x="{X(y) + bw / 2}" y="{Yl(tot[y]) - 14}" font-size="22" font-weight="700" fill="{INK}" text-anchor="{anchor}">{txt}</text>'
    g += foot(80, H - 24, f"Sum of the states that reported each year. {Y1} runs through {THROUGH_TXT} and is provisional (faded bar). Sources: U.S. Public Health Service and CDC disease tables, Project Tycho. {CREDIT}", W)
    g += "</svg>"
    shoot(g, W, H, IMG / "03-us-measles-century.png")
    return tot, peak, low, since


# ---------- social: the national split-tile map, 2015 to 2026 ----------
def gif_national():
    W, H = 1200, 800
    TW, TH, GAP, X0m, Y0m = 84, 62, 5, 120, 150   # 8 rows end near 680, above the two legend lines
    frames = []
    k = D["vax"]["kinder"]["mmr"]
    for y in range(2015, Y1 + 1):
        i = y - Y0
        total = sum(D["cases"]["measles"][s][i] or 0 for s in STATES)
        below = sum(1 for s in STATES if s != "DC" and str(y) in k.get(s, {}) and k[s][str(y)][0] < 95)
        dc = str(y) in k.get("DC", {}) and k["DC"][str(y)][0] < 95
        g = svg_open(W, H)
        g += f'<text x="60" y="70" font-size="34" font-weight="700" fill="{INK}" font-family="{SERIF}">Measles and vaccination, state by state</text>'
        g += f'<text x="{W - 60}" y="80" font-size="72" font-weight="700" fill="{INK}" text-anchor="end">{y}</text>'
        g += f'<text x="60" y="112" font-size="22" fill="{INK2}">{fmt(total)} measles cases{f" through {THROUGH_TXT}" if y == Y1 else ""} · {below} states{" plus DC" if dc else ""} below 95% of kindergartners vaccinated{" (no figures for 2010-11)" if str(y) not in k.get("UT", {}) else ""}</text>'
        for st, s in STATES.items():
            p = k.get(st, {}).get(str(y))
            v = p[0] if p else None
            c, pop = D["cases"]["measles"][st][i], D["pop"][st][i]
            r = c / pop * 1e5 if c is not None and pop else None
            x, yy = X0m + s["c"] * (TW + GAP), Y0m + s["r"] * (TH + GAP)
            g += (f'<g transform="translate({x},{yy})"><clipPath id="c{st}"><rect width="{TW}" height="{TH}" rx="5"/></clipPath>'
                  f'<g clip-path="url(#c{st})"><path d="M0,0H{TW}L0,{TH}Z" fill="{cov_fill(v)}"/><path d="M{TW},0V{TH}H0Z" fill="{rate_fill(r)}"/>'
                  f'<line x1="{TW}" y1="0" x2="0" y2="{TH}" stroke="{BG}" stroke-width="1.5"/></g>'
                  f'<text x="7" y="20" font-size="15" font-weight="700" fill="{INK2 if v is None else "#121212"}">{st}</text></g>')
        g += (f'<text x="60" y="{H - 74}" font-size="18" fill="{INK2}">Top-left half: kindergartners with the measles vaccine (<tspan fill="{GREEN}">95%+</tspan> <tspan fill="{AMBER}">90 to 94.9%</tspan> <tspan fill="{RED}">under 90%</tspan>). Dark gray: no figure.</text>'
              f'<text x="60" y="{H - 48}" font-size="18" fill="{INK2}">Bottom-right half: measles cases per 100,000 residents (<tspan fill="{RED}">over 1</tspan> <tspan fill="{AMBER}">0.1 to 1</tspan> <tspan fill="{GREEN}">under 0.1</tspan>).</text>')
        g += f'<text x="60" y="{H - 20}" font-size="17" fill="{INK3}">{Y1} runs through {THROUGH_TXT}; its rates use {Y1 - 1} population. Sources: CDC. {CREDIT}</text></svg>'
        f = TMP / f"nat-{y}.png"
        shoot(g, W, H, f)
        frames.append(f)
    make_gif(frames, [900] * (len(frames) - 1) + [4000], SOC / "national-2015-2026.gif")


def make_gif(frames, ms, out):
    code = ("import sys,json\nfrom PIL import Image\nfs=json.loads(sys.argv[1]);ms=json.loads(sys.argv[2])\n"
            "ims=[Image.open(f).convert('RGB').quantize(colors=128,method=Image.Quantize.MEDIANCUT) for f in fs]\n"
            "ims[0].save(sys.argv[3],save_all=True,append_images=ims[1:],duration=ms,loop=0,optimize=True)\n")
    subprocess.run([str(PIL_PY), "-c", code, json.dumps([str(f) for f in frames]), json.dumps(ms), str(out)], check=True)


if __name__ == "__main__":
    for p in (IMG, SOC, TMP):
        p.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:] == ["cycle"]:   # only the one-state-at-a-time social GIF
        gif_cycle()
        sys.exit()
    cov, ut_cases = chart_utah()
    chart_six()
    tot, peak, low, since = chart_century()
    gif_six()
    gif_national()
    print("Utah coverage:", cov)
    print("Utah cases:", ut_cases)
    print("six states:", SIX, {st: [int(cm[(cm.st == st) & (cm.year == y)].cases.sum()) for y in (YEAR_A, YEAR_B)] for st in SIX})
    print(f"U.S.: peak {tot[peak]:,} in {peak}; low {tot[low]:,} in {low}; {Y1} {tot[Y1]:,}, most since {since}")
    print("through", THROUGH_TXT, "| county through", CM_TXT)
