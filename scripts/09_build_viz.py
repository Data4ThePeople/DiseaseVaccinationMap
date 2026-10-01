"""Inline the data into the page template: viz/template.html + viz/data.json -> dist/index.html."""
from common import ROOT

if __name__ == "__main__":
    tpl = (ROOT / "viz" / "template.html").read_text()
    data = (ROOT / "viz" / "data.json").read_text()
    assert tpl.count("/*__DATA__*/null") == 1
    html = tpl.replace("/*__DATA__*/null", data.replace("</", "<\\/"))
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "index.html").write_text(html)
    print("dist/index.html", len(html), "bytes")
