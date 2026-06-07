from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry file safely on Vercel
DATA_PATH = Path(__file__).parent.parent / "telemetry.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/")
async def metrics(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 3),
            "p95_latency": round(float(np.percentile(latencies, 95)), 3),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return result
