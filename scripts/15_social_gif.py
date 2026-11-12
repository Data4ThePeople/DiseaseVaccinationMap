"""Social GIF for the map post: the live map, measles, one frame per year from 2010 to the last year.

Each frame is a headless Chrome screenshot of dist/index.html opened at that year (#y=YYYY), so the GIF shows the tool
exactly as readers see it. Each year holds 0.8 seconds; the last year holds 5.

Output: posts/disease-vaccination-viz/social/map-measles-2010-2026.gif
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "viz" / "data.json").read_text())
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PIL_PY = Path.home() / ".claude/tools/prismic/.venv/bin/python"
TMP = ROOT / "data" / "tmp" / "social-map"
OUT = ROOT / "posts" / "disease-vaccination-viz" / "social" / f"map-measles-2010-{D['y1']}.gif"
W, H = 1280, 820   # wide enough for the one-screen layout; the stage fills the window height

TMP.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
frames = []
for y in range(2010, D["y1"] + 1):
    p = TMP / f"{y}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                    "--virtual-time-budget=4000", f"--screenshot={p}", (ROOT / "dist" / "index.html").as_uri() + f"#d=measles&y={y}"],
                   check=True, capture_output=True)
    frames.append(p)
ms = [800] * (len(frames) - 1) + [5000]
code = ("import sys,json\nfrom PIL import Image\nfs=json.loads(sys.argv[1]);ms=json.loads(sys.argv[2])\n"
        "ims=[Image.open(f).convert('RGB').resize((1200,round(Image.open(f).height*1200/Image.open(f).width)),Image.LANCZOS)"
        ".quantize(colors=128,method=Image.Quantize.MEDIANCUT) for f in fs]\n"
        "ims[0].save(sys.argv[3],save_all=True,append_images=ims[1:],duration=ms,loop=0,optimize=True)\n")
subprocess.run([str(PIL_PY), "-c", code, json.dumps([str(f) for f in frames]), json.dumps(ms), str(OUT)], check=True)
print(OUT, f"{len(frames)} frames, {OUT.stat().st_size // 1024} KB")
