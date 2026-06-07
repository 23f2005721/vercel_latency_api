from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA = json.loads(
    Path("telemetry.json").read_text()
)

@app.post("/")
async def metrics(payload: dict):

    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:

        rows = [
            r for r in DATA
            if r["region"] == region
        ]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies)/len(latencies), 3),
            "p95_latency": round(float(np.percentile(latencies,95)), 3),
            "avg_uptime": round(sum(uptimes)/len(uptimes), 3),
            "breaches": sum(
                1 for x in latencies
                if x > threshold
            )
        }

    return result
