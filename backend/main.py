from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import advisory, environmental, health, risk, simulation

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="CropHeat AI",
    description="Turning hyperlocal climate intelligence into crop-specific decisions.",
    version="0.1.0-stage3",
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(environmental.router)
app.include_router(risk.router)
app.include_router(simulation.router)
app.include_router(advisory.router)
app.include_router(health.router)


@app.get("/health")
def health():
    return {"status": "ok", "stage": "2-3: /api/environment, /api/risk"}