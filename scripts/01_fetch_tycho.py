"""Download every Project Tycho 2.0 United States condition file from Zenodo.

Skips COVID-19 (77 MB, not used) and the two older multi-disease bundles.
Zenodo allows 25 results a page without a login.
"""
import json
import urllib.parse
import urllib.request

from common import RAW, UA, download

OUT = RAW / "tycho"
Q = 'communities:projecttycho AND title:"UNITED STATES OF AMERICA"'


def index():
    rows, page = [], 1
    while True:
        url = "https://zenodo.org/api/records?" + urllib.parse.urlencode({"q": Q, "size": 25, "page": page})
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})))
        hits = d["hits"]["hits"]
        if not hits:
            break
        for h in hits:
            for f in h.get("files", []):
                if f["key"].endswith(".zip"):
                    rows.append({"record": h["id"], "title": h["metadata"]["title"], "file": f["key"],
                                 "size": f["size"], "doi": h.get("doi") or h["metadata"].get("doi")})
        if len(rows) >= d["hits"]["total"]:
            break
        page += 1
    return rows


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rows = index()
    keys = [r["file"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate file names in the Zenodo index"
    (OUT / "_index.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        if r["file"].startswith("US.840539006") or "Level" in r["file"]:
            continue
        download(f"https://zenodo.org/api/records/{r['record']}/files/{r['file']}/content", OUT / r["file"])
    print(len(list(OUT.glob("US.*.zip"))), "files")
