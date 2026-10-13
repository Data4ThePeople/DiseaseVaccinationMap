"""Kindergarten MMR coverage before and after five states changed their school exemption rules.

Reads data/vaccination.csv (series "kinder", vaccine "mmr": CDC SchoolVaxView, as states reported).
The year is the spring of the school year (2017 = 2016-17). `first` is the first school year the new
rule applied to entering kindergartners. Rule dates and sources are in RULES below.

Output: analysis/charts/exemption_rules_mmr.svg and exemption_rules_numbers.txt (the PNG is a
screenshot of the SVG).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis" / "charts"

RULES = [  # state, name, first school year under the new rule (spring year), what changed, source
    ("CA", "California", 2017, "Ended personal belief exemptions",
     "SB 277, signed June 30, 2015; applied to school entry from July 1, 2016",
     "https://www.leginfo.ca.gov/pub/15-16/bill/sen/sb_0251-0300/sb_277_bill_20150618_amended_asm_v93.htm"),
    ("NY", "New York", 2020, "Ended its religious exemption",
     "Signed June 13, 2019, in effect at once",
     "https://bsk.com/news-insights/a-repeal-of-the-religious-exemption-to-vaccinationsnbsp"),
    ("ME", "Maine", 2022, "Ended non-medical exemptions",
     "Public Law 2019, ch. 154 (LD 798); upheld by voters in March 2020; in effect September 1, 2021",
     "https://www1.maine.gov/dhhs/mecdc/infectious-disease/immunization/maine-vaccine-exemption-law-changes.shtml"),
    ("CT", "Connecticut", 2023, "Ended its religious exemption",
     "Signed April 2021; in effect with the 2022-23 school year; students who already had one kept it",
     "https://www.foxnews.com/us/connecticut-ends-religious-vaccine-exemption"),
    ("MS", "Mississippi", 2024, "Added a religious exemption",
     "Federal court order, April 2023 (Bosarge v. Edney); exemption offered from July 15, 2023",
     "https://msdh.ms.gov/Page/resources/19957.pdf"),
]
BLUE, ORANGE, INK, INK2, INK3, RULE = "#256abf", "#c96a12", "#121212", "#55534e", "#8a8780", "#e3e2dd"
Y0, Y1, V0, V1 = 2010, 2026, 88.0, 100.0
sy = lambda y: "%d-%02d" % (y - 1, y % 100)  # noqa: E731


def main():
    v = pd.read_csv(ROOT / "data" / "vaccination.csv")
    k = v[(v.series == "kinder") & (v.vaccine == "mmr") & v.estimate.notna()]
    pw, ph, gap, ml, mt = 232, 190, 26, 44, 112
    W, H = ml + len(RULES) * pw + (len(RULES) - 1) * gap + 16, mt + ph + 96
    X = lambda i, y: ml + i * (pw + gap) + (y - Y0) / (Y1 - Y0) * pw  # noqa: E731
    Y = lambda val: mt + (V1 - val) / (V1 - V0) * ph  # noqa: E731
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Helvetica Neue,Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<text x="{ml - 30}" y="30" font-family="Georgia,serif" font-weight="700" font-size="21" fill="{INK}">Measles vaccination among kindergartners, before and after five states changed their exemption rules</text>',
         f'<text x="{ml - 30}" y="52" font-size="13.5" fill="{INK2}">Share of kindergartners with the MMR vaccine, school years 2009-10 to 2025-26. The shaded years are under the new rule. The dashed line is 95%, the national target.</text>']
    lines = ["Kindergarten MMR coverage, last school year before the rule change and after", ""]
    for i, (st, name, first, what, detail, src) in enumerate(RULES):
        d = k[k.st == st].sort_values("year")
        d = d[d.year.between(Y0, Y1)]
        col = ORANGE if st == "MS" else BLUE
        x0, x1 = X(i, Y0), X(i, Y1)
        xr = X(i, first - 0.5)
        s.append(f'<text x="{x0}" y="{mt - 30}" font-family="Georgia,serif" font-weight="700" font-size="16" fill="{INK}">{name}</text>')
        s.append(f'<text x="{x0}" y="{mt - 13}" font-size="12" fill="{col}" font-weight="700">{what}, {sy(first)}</text>')
        s.append(f'<rect x="{xr}" y="{mt}" width="{x1 - xr + 6}" height="{ph}" fill="{col}" opacity="0.09"/>')
        for val in (90, 95, 100):
            dash = ' stroke-dasharray="4 3"' if val == 95 else ""
            s.append(f'<line x1="{x0}" x2="{x1 + 6}" y1="{Y(val)}" y2="{Y(val)}" stroke="{INK2 if val == 95 else RULE}" stroke-width="1"{dash}/>')
            if i == 0:
                s.append(f'<text x="{x0 - 6}" y="{Y(val) + 4}" text-anchor="end" font-size="11" fill="{INK3}">{val}%</text>')
        s.append(f'<line x1="{xr}" x2="{xr}" y1="{mt}" y2="{mt + ph}" stroke="{col}" stroke-width="1.2"/>')
        for yy in (2010, 2015, 2020, 2025):
            s.append(f'<text x="{X(i, yy)}" y="{mt + ph + 15}" text-anchor="middle" font-size="10.5" fill="{INK3}">{yy}</text>')
        # line, broken where a school year has no figure
        seg, prev = [], None
        for r in d.itertuples():
            if prev is not None and r.year - prev > 1:
                s.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="{col}" stroke-width="2"/>')
                seg = []
            seg.append(f"{X(i, r.year):.1f},{Y(r.estimate):.1f}")
            prev = r.year
        s.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="{col}" stroke-width="2"/>')
        for r in d.itertuples():
            census = str(r.method).strip().lower() == "census"
            s.append(f'<circle cx="{X(i, r.year):.1f}" cy="{Y(r.estimate):.1f}" r="2.8" fill="{col if census else "#fff"}" stroke="{col}" stroke-width="1.3"/>')
        before, after1, last = d[d.year == first - 1].iloc[0], d[d.year == first].iloc[0], d.iloc[-1]
        up = last.estimate >= before.estimate
        s.append(f'<text x="{X(i, first - 1) - 5}" y="{Y(before.estimate) + 17}" text-anchor="end" font-size="12" font-weight="700" fill="{INK}">{before.estimate:.1f}%</text>')
        s.append(f'<text x="{x1 + 4}" y="{Y(last.estimate) + (-9 if up else 17)}" text-anchor="end" font-size="12" font-weight="700" fill="{INK}">{last.estimate:.1f}%</text>')
        lines.append(f"{name}: {what.lower()}, first school year {sy(first)}. {detail}. Source: {src}")
        lines.append(f"  {sy(first - 1)} (last year before): {before.estimate:.1f}%   {sy(first)}: {after1.estimate:.1f}%   {sy(int(last.year))} (latest): {last.estimate:.1f}%"
                     f"   change, last year before to latest: {last.estimate - before.estimate:+.1f} points")
        notfull = [sy(int(r.year)) for r in d.itertuples() if str(r.method).strip().lower() != "census"]
        lines.append(f"  school years not a count of all schools: {', '.join(notfull) if notfull else 'none'}")
        lines.append("")
    fy = mt + ph + 40
    notes = ["Labels give the last school year before the change and 2025-26. Years run by the spring of the school year; 2010-11 has no state figures. Hollow dots are years a state",
             "did not count every school (a voluntary or partial response). Other things changed in these years too, including the 2019 measles outbreaks and the pandemic, so the",
             "chart shows what followed each rule, not what caused the change. Maine ended religious and philosophical exemptions. Connecticut let students who already had a religious exemption keep it.",
             "Source: CDC SchoolVaxView, kindergarten coverage as reported by states. Chart: Data 4 The People."]
    for j, t in enumerate(notes):
        s.append(f'<text x="{ml - 30}" y="{fy + j * 15}" font-size="11.5" fill="{INK2}">{t}</text>')
    s.append("</svg>")
    OUT.mkdir(exist_ok=True)
    (OUT / "exemption_rules_mmr.svg").write_text("\n".join(s))
    (OUT / "exemption_rules_numbers.txt").write_text("\n".join(lines))
    print("\n".join(lines))
    print(W, H)


if __name__ == "__main__":
    main()
