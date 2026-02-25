import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def parse_sched_when(s: str):
    if s.startswith("EVERY:"):
        v = s[6:]
        if v.endswith("h"):
            return "EVERY", int(v[:-1]) * 3600
        if v.endswith("m"):
            return "EVERY", int(v[:-1]) * 60
        raise ValueError("bad EVERY")
    if s.startswith("WEEKDAYS:"):
        rest = s[9:]
        days_part, time_part = rest.split("/", 1)
        days = []
        for d in days_part.split(":"):
            idx = "MO TU WE TH FR SA SU".split().index(d)
            days.append(idx)
        h, m = [int(x) for x in time_part.split(":")]
        return "WEEKDAYS", days, h, m
    if s.startswith("MONTHDAY:"):
        rest = s[9:]
        day_str, time_part = rest.split("/", 1)
        day = int(day_str)
        h, m = [int(x) for x in time_part.split(":")]
        return "MONTHDAY", day, h, m
    raise ValueError("bad sched_when")


def calculate_next_run(sched_when: str, last_run_ts: float, ws_timezone: str, random_seed: str) -> float:
    tz = ZoneInfo(ws_timezone)
    kind, *p = parse_sched_when(sched_when)
    if kind == "EVERY":
        period = p[0]
        raw = 0
        for ch in random_seed:
            raw = (raw * 131 + ord(ch)) & 0xFFFFFFFF
        shift = (raw / 2**32) * period
        delta = (period - (last_run_ts - shift) % period) % period
        if delta == 0:
            delta = period
        next_t = last_run_ts + delta
        return next_t

    elif kind == "WEEKDAYS":
        last_dt = datetime.fromtimestamp(last_run_ts, tz=tz)
        days, h, m = p
        day = last_dt.date()
        while True:
            candidate = (
                datetime.combine(day, datetime.min.time(), tz)
                .replace(hour=h, minute=m)
            )
            if candidate > last_dt and candidate.weekday() in days:
                dt = candidate
                break
            day += timedelta(days=1)

    elif kind == "MONTHDAY":
        last_dt = datetime.fromtimestamp(last_run_ts, tz=tz)
        day_num, h, m = p
        y = last_dt.year
        mo = last_dt.month
        while True:
            if day_num == -1:
                nm = datetime(y, mo, 28, tzinfo=tz) + timedelta(days=4)
                d = (nm - timedelta(days=nm.day)).day
            else:
                d = day_num
            try:
                candidate = datetime(y, mo, d, h, m, tzinfo=tz)
            except ValueError:
                candidate = None
            if candidate and candidate > last_dt:
                dt = candidate
                break
            if mo == 12:
                y += 1
                mo = 1
            else:
                mo += 1
    else:
        return datetime.max.timestamp()
    return dt.timestamp()


def tests():
    # pip install tzlocal to run this (not necessary for the rest of the code)
    import tzlocal
    print(f"Parse EVERY:2h: {parse_sched_when('EVERY:2h')}")
    print(f"Parse WEEKDAYS:MO:FR/10:30: {parse_sched_when('WEEKDAYS:MO:FR/10:30')}")
    print(f"Parse MONTHDAY:-1/23:59: {parse_sched_when('MONTHDAY:-1/23:59')}")

    def test(when: str):
        now = time.time()
        nonlocal local_timezone_name, random_seed
        next_ts = calculate_next_run(when, now, local_timezone_name, random_seed)
        print("%s in timezone %s seed %s" % (when, local_timezone_name, random_seed))
        print("    %0.1f seconds from now" % (next_ts - now))
        milliseconds = int((next_ts % 1) * 1000)
        print("    %s.%03d local time" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_ts)), milliseconds))

    print()

    local_timezone_name = "UTC"
    random_seed = "xxx"
    test("EVERY:5m")
    test("EVERY:2h")
    random_seed = "yyy"
    test("EVERY:5m")
    test("EVERY:2h")
    time.sleep(0.1)

    print()

    local_timezone_name = str(tzlocal.get_localzone_name())
    test("WEEKDAYS:MO:TU:WE:TH:FR/21:00")
    local_timezone_name = "UTC"
    test("WEEKDAYS:MO:TU:WE:TH:FR/21:00")

    print()

    local_timezone_name = str(tzlocal.get_localzone_name())
    test("MONTHDAY:1/12:00")
    local_timezone_name = "UTC"
    test("MONTHDAY:1/12:00")
    print()

    local_timezone_name = str(tzlocal.get_localzone_name())
    test("MONTHDAY:-1/12:00")
    local_timezone_name = "UTC"
    test("MONTHDAY:-1/12:00")


if __name__ == "__main__":
    tests()
