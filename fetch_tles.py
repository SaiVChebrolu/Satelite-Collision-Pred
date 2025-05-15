import requests

def fetch_tle(url="https://celestrak.com/NORAD/elements/active.txt"):
    resp = requests.get(url)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    sats = []
    for i in range(0, len(lines), 3):
        name, l1, l2 = lines[i], lines[i+1], lines[i+2]
        sats.append((name, l1, l2))
    return sats

if __name__ == "__main__":
    sats = fetch_tle()
    print(f"Fetched {len(sats)} TLEs. Example:\n", sats[0])
