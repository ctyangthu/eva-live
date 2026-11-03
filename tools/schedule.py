"""Parse data/schedule-nw26.txt into a list of flight segments (shared by build.py and check_schedule.py)."""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "data" / "schedule-nw26.txt"
AIRCRAFT = {"77W", "789", "781", "333", "321"}
LINE = re.compile(r"^(BR\d+)\s+([A-Z]{3})\s+(\d\d:\d\d)\s+([A-Z]{3})\s+(\d\d:\d\d)(?:\+(\d))?\s+(D|\?\d|[1-7]+)\s+(\S+)((?:\s+\w+=\S+)*)\s*$")


def parse(path=SCHEDULE):
    segs = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line: continue
        m = LINE.match(line)
        if not m: raise ValueError(f"{path.name}:{n}: cannot parse {raw!r}")
        no, o, dep, d, arr, plus, days, ac, opts = m.groups()
        if ac not in AIRCRAFT: raise ValueError(f"{path.name}:{n}: unknown aircraft {ac}")
        seg = {"no": no, "o": o, "d": d, "dep": dep, "arr": arr, "plus": int(plus or 0), "ac": ac}
        if days == "D": seg["days"] = "1234567"
        elif days.startswith("?"): seg["days"] = None; seg["freq"] = int(days[1:])
        else: seg["days"] = "".join(sorted(set(days)))
        for kv in opts.split():
            k, v = kv.split("=", 1)
            if k not in ("from", "to", "skip"): raise ValueError(f"{path.name}:{n}: unknown option {k}")
            seg[k] = v
        segs.append(seg)
    return segs
