from fastapi import FastAPI
from fetch_tles import fetch_tle
from propagate import propagate_one
from collision_checker import find_conjunctions
from pydantic import BaseModel
from typing import List

app = FastAPI()

class SatellitePosition(BaseModel):
    name: str
    position: List[float]

class Conjunction(BaseModel):
    sat1: str
    sat2: str
    distance: float

@app.get("/api/satellites", response_model=List[str])
def list_sats() -> List[str]:
    return [name.strip() for name, *_ in fetch_tle()]

@app.get("/api/positions", response_model=List[SatellitePosition])
def get_positions() -> List[SatellitePosition]:
    tles = fetch_tle()[:200]
    return [SatellitePosition(name=name.strip(), position=list(propagate_one((name, l1, l2))[1]))
            for name, l1, l2 in tles]

@app.get("/api/conjunctions", response_model=List[Conjunction])
def get_conjunctions(threshold_km: float = 10.0) -> List[Conjunction]:
    tles = fetch_tle()[:200]
    pairs = find_conjunctions(tles, threshold_km)
    results = []
    for i, j in pairs:
        name_i, *_ = tles[i]
        name_j, *_ = tles[j]
        _, pos_i, _ = propagate_one(tles[i])
        _, pos_j, _ = propagate_one(tles[j])
        dist = sum((pi - pj)**2 for pi, pj in zip(pos_i, pos_j))**0.5
        results.append(Conjunction(sat1=name_i.strip(), sat2=name_j.strip(), distance=dist))
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)