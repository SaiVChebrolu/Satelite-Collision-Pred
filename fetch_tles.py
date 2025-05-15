import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_tle_celestrak_gp(group: str = "active", fmt: str = "TLE") -> list:
    """
    Fetch TLEs via CelesTrak GP API (supports 9-digit catalog numbers).
    """
    url = (
        "https://celestrak.org/NORAD/elements/gp.php"
        f"?GROUP={group}&FORMAT={fmt}"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    sats = []
    for i in range(0, len(lines), 3):
        sats.append((lines[i], lines[i+1], lines[i+2]))
    return sats


def fetch_tle_ivanstanojevic() -> list:
    """
    Fetch TLEs from Ivan Stanojevic's public API.
    """
    url = "https://tle.ivanstanojevic.me/api/tle"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    sats = [(sat.get("name"), sat.get("line1"), sat.get("line2")) for sat in data]
    return sats


def fetch_tle_space_track() -> list:
    """
    Fetch TLEs via Space-Track (requires SPACETRACK_USER & PASS in .env).
    """
    user = os.getenv("SPACETRACK_USER")
    pwd = os.getenv("SPACETRACK_PASS")
    if not user or not pwd:
        raise RuntimeError("Space-Track credentials not provided.")
    base = "https://www.space-track.org"
    session = requests.Session()
    session.post(base + "/ajaxauth/login", data={"identity": user, "password": pwd})
    resp = session.get(base + "/basicspacedata/query/class/tle_latest/format/tle")
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    sats = [(lines[i], lines[i+1], lines[i+2]) for i in range(0, len(lines), 3)]
    return sats


def fetch_tle() -> list:
    """
    Try primary CelesTrak GP, then fall back to Ivan's API, then Space-Track.
    """
    try:
        return fetch_tle_celestrak_gp()
    except Exception as e:
        print(f"CelesTrak GP fetch failed: {e}")
    try:
        return fetch_tle_ivanstanojevic()
    except Exception as e:
        print(f"Ivan's API fetch failed: {e}")
    try:
        return fetch_tle_space_track()
    except Exception as e:
        print(f"Space-Track fetch failed: {e}")
    raise RuntimeError("All TLE sources failed.")


if __name__ == "__main__":
    sats = fetch_tle()
    print(f"Fetched {len(sats)} TLEs. Example:\n", sats[0])