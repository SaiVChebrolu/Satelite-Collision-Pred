from sgp4.api import Satrec, WGS72, jday
from datetime import datetime, timezone

def propagate_one(tle: tuple, when: datetime = None) -> tuple:
    """
    Propagate a single satellite using SGP4 to ECI position at given time.
    """
    name, line1, line2 = tle
    sat = Satrec.twoline2rv(line1, line2, WGS72)
    if when is None:
        when = datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    jd, fr = jday(
        when.year, when.month, when.day,
        when.hour, when.minute, when.second + when.microsecond * 1e-6
    )
    e, r, v = sat.sgp4(jd, fr)
    if e != 0:
        raise RuntimeError(f"SGP4 error code {e}")
    return name, r, v

if __name__ == "__main__":
    from fetch_tles import fetch_tle
    tle0 = fetch_tle()[0]
    name, pos, vel = propagate_one(tle0)
    print(name, "pos (km):", pos)
