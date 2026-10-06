"""Rebuild every data file in the project from the original sources, in order.

    python scripts/run_all.py            # everything: download what is missing, extract, build, check
    python scripts/run_all.py --quick    # only what the page needs on top of the committed tables

Downloads go to data/raw/ (git-ignored) and are skipped when the file is already there, so a
second run is fast. A full first run downloads roughly 700 MB and takes a while; the slowest
steps are the CDC weekly file and the scanned CDC annual reports.

Some sources are live and keep changing (CDC's weekly table, the Johns Hopkins trackers, BEA
and Census revisions), so a fresh run can differ slightly from the committed files in recent
years. `git diff --stat data/` after a run shows what moved.

No key is needed: the Census API responses are saved in the repo. CENSUS_API_KEY is only
needed to fetch a year that is not saved yet.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

FULL = [
    ("scripts/01_fetch_tycho.py", "Project Tycho weekly case files (Zenodo)"),
    ("scripts/02_fetch_cdc.py", "CDC weekly cases and vaccination files (data.cdc.gov)"),
    ("scripts/02b_fetch_annual_summaries.py", "CDC final annual tables and scanned summaries, 1956-2023"),
    ("scripts/02c_fetch_geo.py", "State and county shapes"),
    ("scripts/03_build_tycho_annual.py", "Tycho weekly rows to yearly state figures"),
    ("scripts/04_fetch_population_income.py", "BEA population and income"),
    ("scripts/04b_fetch_vax_history.py", "Vaccination history, 1959-2017, and licensure years"),
    ("scripts/05_build_cdc_recent.py", "Yearly state figures from the CDC weekly file"),
    ("scripts/06_build_cases.py", "All case sources combined"),
    ("scripts/07_build_vaccination.py", "Vaccination series"),
    ("scripts/08b_fetch_kpis.py", "State indicators and party control"),
    ("scripts/10_build_county.py", "County vaccination and county measles"),
    ("scripts/08_build_data.py", "Pack the page data"),
    ("scripts/09_build_viz.py", "Write dist/index.html"),
    ("scripts/11_coverage.py", "Source coverage check"),
    ("scripts/12_tieout.py", "Tie-out against the raw files"),
    ("analysis/01_vaccination_and_outbreaks.py", "Findings numbers"),
    ("analysis/02_findings_page.py", "Write dist/findings.html"),
]
QUICK = [
    ("scripts/02c_fetch_geo.py", "State and county shapes"),
    ("scripts/08_build_data.py", "Pack the page data"),
    ("scripts/09_build_viz.py", "Write dist/index.html"),
]

if __name__ == "__main__":
    steps = QUICK if "--quick" in sys.argv else FULL
    t0 = time.time()
    for i, (script, what) in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] {what}  ({script})", flush=True)
        t = time.time()
        r = subprocess.run([PY, str(ROOT / script)], cwd=ROOT / Path(script).parent)
        if r.returncode:
            sys.exit(f"\nStopped: {script} failed (exit {r.returncode}). Fix it and run again; finished downloads are kept.")
        print(f"    done in {time.time() - t:.0f}s", flush=True)
    print(f"\nAll {len(steps)} steps finished in {(time.time() - t0) / 60:.1f} minutes.")
