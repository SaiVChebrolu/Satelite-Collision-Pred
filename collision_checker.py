import sqlite3
import numpy as np
from datetime import datetime, timedelta, timezone
from scipy.spatial import cKDTree
from propagate import propagate_one
from fetch_tles import fetch_tle


def init_db(db_path: str = "collisions.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS collisions (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            sat1 TEXT,
            sat2 TEXT,
            distance REAL
        )
    ''')
    conn.commit()
    return conn


def find_conjunctions(sats: list, threshold_km: float = 10.0, when: datetime = None) -> set:
    """
    Propagate all satellites at a single epoch and return index pairs within threshold_km.
    """
    # propagate positions
    pts = []
    for tle in sats:
        _, pos, _ = propagate_one(tle, when)
        pts.append(pos)
    pts = np.array(pts)
    tree = cKDTree(pts)
    return tree.query_pairs(threshold_km)


def sweep_conjunctions_to_db(
    sats: list,
    years: int = 10,
    step_sec: int = 60,
    threshold_km: float = 10.0,
    db_path: str = "collisions.db"
) -> None:
    """
    Sweep from now to now+years, check every step_sec seconds for conjunctions,
    store and log each event in the SQLite database and print status.
    """
    conn = init_db(db_path)
    c = conn.cursor()
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=365 * years)
    t = start
    while t <= end:
        pairs = find_conjunctions(sats, threshold_km, when=t)
        if pairs:
            for i, j in pairs:
                name_i = sats[i][0].strip()
                name_j = sats[j][0].strip()
                # recompute positions for distance
                _, pos_i, _ = propagate_one(sats[i], t)
                _, pos_j, _ = propagate_one(sats[j], t)
                dist = float(np.linalg.norm(np.array(pos_i) - np.array(pos_j)))
                c.execute(
                    "INSERT INTO collisions (timestamp, sat1, sat2, distance) VALUES (?, ?, ?, ?)",
                    (t.isoformat(), name_i, name_j, dist)
                )
                print(f"[{t.isoformat()}] Collision detected: {name_i} vs {name_j} at {dist:.2f} km")
            conn.commit()
        else:
            print(f"[{t.isoformat()}] No collisions detected")
        t += timedelta(seconds=step_sec)
    conn.close()


if __name__ == "__main__":
    sats = fetch_tle()[:200]
    sweep_conjunctions_to_db(sats)
    print("Sweep complete. Collisions stored in collisions.db")