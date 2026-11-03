"""Sanity-check the timetable: block time from local times + time zones, against great-circle distance.

    python3 tools/check_schedule.py          # flags suspicious segments
    python3 tools/check_schedule.py -v       # prints every segment

Uses the winter date 2026-11-04 (a Wednesday) for UTC offsets. A segment is flagged when its
implied average speed is implausible, which catches a wrong +1/+2 or a typo in a time. Eastbound
transpacific flights ride the jet stream (~930 km/h); cross-strait flights under 1,000 km fly
detours plus taxi time, so they may average under 300 km/h.
"""
import datetime as dt, json, math, sys
from zoneinfo import ZoneInfo
from schedule import ROOT, parse

AP = json.loads((ROOT / "data" / "airports.json").read_text(encoding="utf-8"))["airports"]
BASE = dt.date(2026, 11, 4)


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (AP[a][5], AP[a][6], AP[b][5], AP[b][6]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def block(s):
    t = lambda hm: dt.time(*map(int, hm.split(":")))
    d0 = dt.datetime.combine(BASE, t(s["dep"]), ZoneInfo(AP[s["o"]][7]))
    d1 = dt.datetime.combine(BASE + dt.timedelta(days=s["plus"]), t(s["arr"]), ZoneInfo(AP[s["d"]][7]))
    return (d1 - d0).total_seconds() / 60


def main(verbose):
    segs, bad = parse(), 0
    for s in segs:
        for c in (s["o"], s["d"]):
            if c not in AP: raise SystemExit(f"{s['no']}: unknown airport {c}")
        mins, dist = block(s), km(s["o"], s["d"])
        v = dist / (mins / 60) if mins > 0 else 0
        flag = not ((280 if dist < 1000 else 450) <= v <= 1000)
        bad += flag
        if verbose or flag:
            print(f"{'!!' if flag else '  '} {s['no']:6} {s['o']}-{s['d']}  {s['dep']}-{s['arr']}+{s['plus']}  "
                  f"{int(mins // 60):2d}h{int(mins % 60):02d}  {dist:6.0f} km  {v:4.0f} km/h")
    routes = {tuple(sorted((s["o"], s["d"]))) for s in segs}
    print(f"{len(segs)} segments, {len(routes)} routes, {bad} flagged")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main("-v" in sys.argv) else 0)
