"""Hero image for the post: a simplified national map of measles in the map's last year, 1680x1080.

Each state is split corner to corner, as on the map: top left is kindergarten MMR coverage for the school year
ending that year, bottom right is reported measles cases per 100,000 residents. Same cutoffs and colors as the map.
Every number is read from viz/data.json. Writes an HTML page next to the image and screenshots it with headless Chrome.

Output: posts/disease-vaccination-viz/images/disease-vaccination-viz-hero-source.html and -hero-1680x1080.png
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "viz" / "data.json").read_text())
OUT = ROOT / "posts" / "disease-vaccination-viz" / "images"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

GREEN, AMBER, RED, NOFIG = "#86c383", "#f4c457", "#e2675f", "#2b2e30"
cov_fill = lambda v: NOFIG if v is None else GREEN if v >= 95 else AMBER if v >= 90 else RED
rate_fill = lambda r: NOFIG if r is None else RED if r > 1 else AMBER if r >= 0.1 else GREEN

y = D["y1"]
i = y - D["y0"]
states = D["states"]
mmr = D["vax"]["kinder"]["mmr"]
cells, below95, below90, n_cov, above1, total = [], 0, 0, 0, 0, 0
dc_below = False
for s in states:
    st = s["k"]
    p = mmr.get(st, {}).get(str(y))
    v = p[0] if p else None
    c = D["cases"]["measles"][st][i]
    pop = D["pop"][st][i]
    r = c / pop * 1e5 if c is not None and pop else None
    total += c or 0
    if v is not None:
        n_cov += 1
        below95 += v < 95 and st != "DC"   # DC is not a state; it is named on its own line
        if st == "DC":
            dc_below = v < 95
        below90 += v < 90
    above1 += r is not None and r > 1
    cells.append((s, cov_fill(v), rate_fill(r)))
assert total == sum(D["cases"]["measles"][s["k"]][i] or 0 for s in states)

# the last week CDC's weekly tables cover, as a date: MMWR week 1 is the first Sunday-to-Saturday week with 4+ days in the year
import datetime as dt
j1 = dt.date(D["partial"]["year"], 1, 1)
start = j1 - dt.timedelta(days=(j1.weekday() + 1) % 7) if (j1.weekday() + 1) % 7 <= 3 else j1 + dt.timedelta(days=7 - (j1.weekday() + 1) % 7)
through = start + dt.timedelta(days=D["partial"]["week"] * 7 - 1)
through_txt = f"{through:%B} {through.day}"
school = f"{y - 1}-{str(y)[2:]}"

TW, TH, GAP, X0, Y0 = 80, 68, 6, 650, 236   # 11 columns end at 1590, a 90px margin like the left side
tiles = []
for s, top, bot in cells:
    x, yy = X0 + s["c"] * (TW + GAP), Y0 + s["r"] * (TH + GAP)
    tiles.append(f'<g transform="translate({x},{yy})"><clipPath id="c{s["k"]}"><rect width="{TW}" height="{TH}" rx="5"/></clipPath>'
                 f'<g clip-path="url(#c{s["k"]})"><path d="M0,0H{TW}L0,{TH}Z" fill="{top}"/><path d="M{TW},0V{TH}H0Z" fill="{bot}"/>'
                 f'<line x1="{TW}" y1="0" x2="0" y2="{TH}" stroke="#181A1B" stroke-width="1.5"/></g>'
                 f'<text x="7" y="21" font-size="16" font-weight="700" fill="{"#BBBDC0" if top == NOFIG else "#121212"}">{s["k"]}</text></g>')

def key_row(y0, label, items):
    out = f'<text x="0" y="{y0}" font-size="21" font-weight="700" fill="#BBBDC0">{label}</text>'
    x = 0
    for color, txt, w in items:   # w: the width this swatch and its words take
        out += f'<rect x="{x}" y="{y0 + 14}" width="20" height="20" rx="3" fill="{color}" stroke="{"#8a8c8f" if color == NOFIG else "none"}"/><text x="{x + 28}" y="{y0 + 30}" font-size="19" fill="#BBBDC0">{txt}</text>'
        x += w
    return out

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1080" viewBox="0 0 1680 1080" font-family="Helvetica Neue,Helvetica,Arial,sans-serif">
<rect width="1680" height="1080" fill="#181A1B"/>
<text x="90" y="150" font-size="58" font-weight="700" fill="#EDEEEF" font-family="Georgia,serif">Measles and</text>
<text x="90" y="218" font-size="58" font-weight="700" fill="#EDEEEF" font-family="Georgia,serif">vaccination,</text>
<text x="90" y="286" font-size="58" font-weight="700" fill="#EDEEEF" font-family="Georgia,serif">state by state</text>
<text x="90" y="340" font-size="26" fill="#BBBDC0">{y}, through {through_txt}</text>
<text x="90" y="440" font-size="64" font-weight="700" fill="#EDEEEF">{total:,}</text>
<text x="90" y="478" font-size="23" fill="#BBBDC0">measles cases reported in {y}</text>
<text x="90" y="506" font-size="23" fill="#BBBDC0">through {through_txt} (provisional)</text>
<text x="90" y="600" font-size="64" font-weight="700" fill="#EDEEEF">{below95}</text>
<text x="90" y="638" font-size="23" fill="#BBBDC0">states{", plus DC," if dc_below else ""} below 95% of kindergartners</text>
<text x="90" y="666" font-size="23" fill="#BBBDC0">with the measles vaccine, {school}</text>
<g transform="translate(90,760)">
<rect x="0" y="0" width="100" height="100" rx="5" fill="#2b2e30" stroke="#BBBDC0" stroke-width="1.5"/>
<path d="M100,0L0,100" stroke="#BBBDC0" stroke-width="1.5"/>
<text x="7" y="21" font-size="13" font-weight="700" fill="#BBBDC0">Vaccinated</text>
<text x="93" y="91" font-size="13" font-weight="700" fill="#BBBDC0" text-anchor="end">Cases</text>
</g>
<g transform="translate(210,768)">{key_row(0, "Top left: kindergartners with MMR", [(GREEN, "95%+", 100), (AMBER, "90 to 94.9%", 150), (RED, "under 90%", 130)])}</g>
<g transform="translate(210,838)">{key_row(0, "Bottom right: cases per 100,000", [(RED, "over 1", 100), (AMBER, "0.1 to 1", 150), (GREEN, "under 0.1", 130)])}</g>
<g transform="translate(210,894)">{key_row(-14, "", [(NOFIG, "no figure", 130)])}</g>
{"".join(tiles)}
<text x="1590" y="1010" font-size="19" fill="#8a8c8f" text-anchor="end">Data 4 The People. Sources: CDC weekly disease tables and SchoolVaxView. 2026 rates use 2025 population.</text>
</svg>'''

OUT.mkdir(parents=True, exist_ok=True)
html = OUT / "disease-vaccination-viz-hero-source.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#181A1B}}</style></head><body>{svg}</body></html>')
png = OUT / "disease-vaccination-viz-hero-1680x1080.png"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1680,1080",
                f"--screenshot={png}", html.as_uri()], check=True, capture_output=True)
print(png, f"| {y} through {through_txt}: {total:,} cases; {below95} states{' plus DC' if dc_below else ''} below 95% ({n_cov} with a figure), {below90} below 90%; {above1} states above 1 per 100,000")
