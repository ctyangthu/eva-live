"""Inline timetable, airports and map data into src/app.html and write the site into dist/.

    python3 tools/build.py

dist/index.html     standalone page (GitHub Pages, or open directly in a browser)
dist/artifact.html  page body only, for hosts that add their own document skeleton
"""
import json, pathlib
from schedule import ROOT, parse

src = (ROOT / "src" / "app.html").read_text(encoding="utf-8")
segs = parse()
airports = json.loads((ROOT / "data" / "airports.json").read_text(encoding="utf-8"))
airports.pop("_fields", None)
geo = json.loads((ROOT / "data" / "map.json").read_text(encoding="utf-8"))

compact = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
flights = {"season": "NW26", "valid": ["2026-10-25", "2027-03-27"], "updated": "2026-11-04", "segs": segs}
body = (src.replace("__FLIGHTS_JSON__", compact(flights))
           .replace("__AIRPORTS_JSON__", compact(airports))
           .replace("__MAP_JSON__", compact(geo)))
assert "__FLIGHTS_JSON__" not in body and "__AIRPORTS_JSON__" not in body and "__MAP_JSON__" not in body

# title, fonts and styles come before the app markup; they belong in <head>
split = body.index('<div class="app">')
standalone = (
    '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="description" content="依長榮航空 2026/27 冬季國際線班表，在世界地圖上推算各航班位置，並提供出發／抵達看板、時刻表與航線網路。非官方展示。">\n'
    + body[:split] + "</head>\n<body>\n" + body[split:] + "\n</body>\n</html>\n"
)
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
(dist / "index.html").write_text(standalone, encoding="utf-8")
(dist / "artifact.html").write_text(body, encoding="utf-8")
routes = {tuple(sorted((s["o"], s["d"]))) for s in segs}
print(f"dist/index.html + dist/artifact.html written: {len(body.encode('utf-8')) / 1024:.1f} KB, "
      f"{len(segs)} segments, {len(routes)} routes")
