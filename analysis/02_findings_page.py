"""Build the shareable findings page (dist/findings.html, published by GitHub Pages) from the same tables as FINDINGS.md.
The two charts are drawn here as inline SVG, so the page needs no library and no network."""
import html
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# ---- county coverage small multiples ----
cm = pd.read_csv(ROOT / "data/county_mmr.csv", dtype={"fips": str})
jm = pd.read_csv(ROOT / "data/raw/jhu/measles_county_all_updates.csv", dtype=str)
jm["fips"], jm["y"], jm["n"] = jm.location_id.str.zfill(5), jm.date.str[:4].astype(int), jm.value.astype(int)
cases = jm.pivot_table(index="fips", columns="y", values="n", aggfunc="sum", fill_value=0)
COUNTIES = [("04015", "Mohave County, Ariz."), ("45083", "Spartanburg County, S.C."), ("48165", "Gaines County, Tex."),
            ("42071", "Lancaster County, Pa."), ("12021", "Collier County, Fla."), ("49053", "Washington County, Utah")]
Y0, Y1, V0, V1 = 2018, 2025, 70, 100
W, H, ML, MR, MT, MB = 300, 150, 34, 10, 10, 22


def county_svg(fips):
    s = cm[cm.fips == fips].set_index("year").pct
    x = lambda y: ML + (y - Y0) / (Y1 - Y0) * (W - ML - MR)  # noqa: E731
    yy = lambda v: MT + (V1 - v) / (V1 - V0) * (H - MT - MB)  # noqa: E731
    g = []
    for v in (70, 80, 90, 100):
        g.append(f'<line x1="{ML}" x2="{W - MR}" y1="{yy(v):.1f}" y2="{yy(v):.1f}" class="grid"/>'
                 f'<text x="{ML - 6}" y="{yy(v) + 3.5:.1f}" class="tick" text-anchor="end">{v}%</text>')
    g.append(f'<line x1="{ML}" x2="{W - MR}" y1="{yy(95):.1f}" y2="{yy(95):.1f}" class="ref"/>')
    for y, lab in ((2018, "2017-18"), (2025, "2024-25")):
        g.append(f'<text x="{x(y):.1f}" y="{H - 6}" class="tick" text-anchor="{"start" if y == Y0 else "end"}">{lab}</text>')
    pts = [(x(y), yy(v)) for y, v in s.items()]
    g.append('<path d="M' + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '" class="line"/>')
    falling_end = len(s) > 1 and s.iloc[-1] < s.iloc[-2]   # put the end label under a falling line so it clears it
    for (a, b), (y, v) in zip([pts[0], pts[-1]], [(s.index[0], s.iloc[0]), (s.index[-1], s.iloc[-1])]):
        end = y != s.index[0]
        ty = b + 16 if end and falling_end else b - 7
        g.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3.5" class="dot"/>'
                 f'<text x="{a + (-6 if end else 6):.1f}" y="{ty:.1f}" class="val" text-anchor="{"end" if end else "start"}">{v:.1f}%</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Kindergarten MMR coverage, {s.index[0]-1}-{str(s.index[0])[2:]} to 2024-25">{"".join(g)}</svg>'


cards = []
for f, name in COUNTIES:
    c25 = int(cases.loc[f, 2025]) if f in cases.index else 0
    c26 = int(cases.loc[f, 2026]) if f in cases.index else 0
    note = "Utah reports cases by health district, so county counts are not available." if f == "49053" else \
        f"Measles cases: <b>{c25:,}</b> in 2025, <b>{c26:,}</b> in 2026"
    cards.append(f'<figure class="county"><figcaption><span class="cname">{html.escape(name)}</span><span class="ccases">{note}</span></figcaption>{county_svg(f)}</figure>')

# ---- mumps national line ----
cs = pd.read_csv(ROOT / "data/cases_state_year.csv")
mu = cs[cs.disease == "mumps"].groupby("year").cases.sum()
MW, MH, mML, mMR, mMT, mMB = 760, 260, 58, 16, 16, 28
my0, my1, mv1 = 1965, 2025, 200000
mx = lambda y: mML + (y - my0) / (my1 - my0) * (MW - mML - mMR)  # noqa: E731
mv = lambda v: mMT + (mv1 - v) / mv1 * (MH - mMT - mMB)  # noqa: E731
mg = []
for v in (0, 50000, 100000, 150000, 200000):
    mg.append(f'<line x1="{mML}" x2="{MW - mMR}" y1="{mv(v):.1f}" y2="{mv(v):.1f}" class="grid"/>'
              f'<text x="{mML - 8}" y="{mv(v) + 3.5:.1f}" class="tick" text-anchor="end">{v // 1000}k</text>')
for y in (1970, 1980, 1990, 2000, 2010, 2020):
    mg.append(f'<text x="{mx(y):.1f}" y="{MH - 8}" class="tick" text-anchor="middle">{y}</text>')
mg.append('<path d="M' + "L".join(f"{mx(y):.1f},{mv(v):.1f}" for y, v in mu.items()) + '" class="mline"/>')
# CDC's own national figures from the 1989 ACIP report, as points
for y, v, lab, anc in ((1967, 185691, "1967: 185,691", "start"), (1985, 2982, "", "start"), (1987, 12848, "1987: 12,848", "start")):
    mg.append(f'<circle cx="{mx(y):.1f}" cy="{mv(v):.1f}" r="4" class="cdc"/>')
    if lab:
        mg.append(f'<text x="{mx(y) + 8:.1f}" y="{mv(v) - 8:.1f}" class="val" text-anchor="{anc}">{lab}</text>')
mg.append(f'<line x1="{mx(1967):.1f}" x2="{mx(1967):.1f}" y1="{mMT}" y2="{MH - mMB}" class="ref"/>'
          f'<text x="{mx(1967) + 6:.1f}" y="{MH - mMB - 8:.1f}" class="tick">vaccine licensed</text>')
mumps_svg = f'<svg viewBox="0 0 {MW} {MH}" role="img" aria-label="Reported mumps cases in the United States, 1968 to 2025">{"".join(mg)}</svg>'

tpl = (ROOT / "analysis" / "findings_template.html").read_text()
page = tpl.replace("<!--COUNTY_CARDS-->", "\n".join(cards)).replace("<!--MUMPS_SVG-->", mumps_svg)
head, body = page.split("<main", 1)   # template = title, font links and style, then the page body
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<meta name="description" content="Places where school vaccination coverage dropped and a measles outbreak followed, and the story behind the mumps record. Working findings from Data 4 The People.">\n'
       + head + '</head>\n<body>\n<main' + body + '\n</body>\n</html>\n')
(ROOT / "dist" / "findings.html").write_text(doc)   # served by GitHub Pages next to the map
print("dist/findings.html", len(doc))
