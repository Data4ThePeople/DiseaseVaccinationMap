"""State and county shapes: us-atlas counties-10m (Census cartographic boundary files as TopoJSON)."""
from common import RAW, download

if __name__ == "__main__":
    p = download("https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json", RAW / "geo" / "counties-10m.json")
    print(p, p.stat().st_size)
