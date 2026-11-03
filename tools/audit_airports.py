"""Compare the timetable with the flights the Taiwanese airports publish themselves.

    python3 tools/audit_airports.py

Taoyuan publishes yesterday to tomorrow; Songshan, Kaohsiung and Taichung publish today. Numbers
with four digits (BR2xxx, BR3xxx) are codeshares flown by other airlines and are ignored, as is a
letter suffix such as BR35D, which marks a delayed operation. Run it on different weekdays: each
run only sees the days the airports list.
"""
import datetime as dt, json, re, urllib.request
from zoneinfo import ZoneInfo
from schedule import parse

UA = {"User-Agent": "Mozilla/5.0 (compatible; eva-live timetable audit)"}
TSA = "https://www.tsa.gov.tw/api/airFlyTab/Paging"


def get(url, data=None):
    headers = dict(UA, **({"Content-Type": "application/json"} if data else {}))
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers)
    return urllib.request.urlopen(req, timeout=40).read()


def own(no):
    """BR123 for an EVA-operated flight, None for a codeshare or a delayed operation."""
    m = re.fullmatch(r"(?:BR)?0*(\d{1,3})", no.strip())
    return "BR" + m.group(1) if m else None


def hhmm(t):
    return t[:2] + ":" + t[-2:] if ":" not in t else t[:5]


def taoyuan():
    rows = [[c.strip() for c in l.split(",")] for l in get("https://www.taoyuan-airport.com/uploads/flightx/a_flight_v4.txt").decode("big5", "replace").splitlines() if l.strip()]
    for r in rows:
        if r[2] == "BR" and own(r[4]):
            yield "TPE", dt.date(*map(int, r[6].split("/"))), "dep" if r[1] == "D" else "arr", own(r[4]), r[7][:5], r[10]


def kaohsiung(today):
    for io, name, code in (("dep", "INTDEP", "goalAirportCode"), ("arr", "INTARR", "upAirportCode")):
        for r in json.loads(get(f"https://www.kia.gov.tw/Announce/NewsArea/InstantSchedule_{name}.json").decode("utf-8-sig")):
            if r["airLineNum"].startswith("BR") and own(r["airLineNum"]):
                yield "KHH", today, io, own(r["airLineNum"]), hhmm(r["expectTime"]), r[code]


def songshan(today):
    for io, n, sort, time_key, other in (("dep", 1, "ExpectDepartureTime", "ExpectDepartureTime", "GoalAirportName"), ("arr", 2, "ExpectArrivalTime", "ExpectArrivalTime", "UpAirportName")):
        body = {"AirFlyLine": 1, "AirFlyIO": n, "Limit": 999, "Culture": 1, "FlightNumber": None, "AirLineCode": None, "AirportCode": None, "Sort": sort, "Order": "asc"}
        for r in json.loads(get(TSA, body))["rows"]:
            if r["FlightNumber"].startswith("BR") and own(r["FlightNumber"]):
                yield "TSA", today, io, own(r["FlightNumber"]), hhmm(r[time_key]), r[other][-3:]


def taichung(today):
    for io, n, code, key in (("dep", 1, "goalAirportCode", "expectDepartureTime"), ("arr", 2, "upAirportCode", "expectArrivalTime")):
        for r in json.loads(get(f"https://www.tca.gov.tw/?act=fids&code=airflytab&Flyline=1&FlyIO={n}").decode("utf-8-sig"))["Data"]:
            if r["AirLineIATA"] == "BR" and own(r["airLineNum"]):
                yield "RMQ", today, io, own(r["airLineNum"]), hhmm(r[key]), r[code]


def operates(s, d):
    k = d.isoformat()
    return bool(s["days"]) and str(d.isoweekday()) in s["days"] and not (s.get("from") and k < s["from"]) \
        and not (s.get("to") and k > s["to"]) and k not in s.get("skip", "").split(",")


def expected(segs, airport, day, io):
    for s in segs:
        if io == "dep" and s["o"] == airport and operates(s, day):
            yield s["no"], s["dep"], s["d"]
        if io == "arr" and s["d"] == airport and operates(s, day - dt.timedelta(days=s["plus"])):
            yield s["no"], s["arr"], s["o"]


def main():
    segs, today = parse(), dt.datetime.now(ZoneInfo("Asia/Taipei")).date()
    seen = {}
    for feed in (taoyuan(), kaohsiung(today), songshan(today), taichung(today)):
        for airport, day, io, no, time, other in feed:
            seen[airport, day, io, no] = (time, other)
    days = sorted({k[:3] for k in seen} | {(a, today, io) for a in ("KHH", "TSA", "RMQ") for io in ("dep", "arr")})
    missing, extra, moved, checked = [], [], [], 0
    for airport, day, io in days:
        exp = {no: (t, o) for no, t, o in expected(segs, airport, day, io)}
        got = {k[3]: v for k, v in seen.items() if k[:3] == (airport, day, io)}
        checked += len(got)
        tag = f"{day:%m/%d} {airport} {io}"
        missing += [f"{tag} {n} {got[n][0]} {got[n][1]}" for n in sorted(set(got) - set(exp))]
        extra += [f"{tag} {n} {exp[n][0]} {exp[n][1]}" for n in sorted(set(exp) - set(got))]
        moved += [f"{tag} {n} published {got[n][0]}, timetable {exp[n][0]}" for n in sorted(set(got) & set(exp)) if got[n] != exp[n]]
    print(f"{checked} EVA-operated flights published, {len(segs)} segments in the timetable")
    for title, lines in (("published but not in the timetable", missing), ("in the timetable but not published", extra), ("different time or airport", moved)):
        print(f"\n{title}: {len(lines)}")
        for l in lines: print("  " + l)


if __name__ == "__main__":
    main()
