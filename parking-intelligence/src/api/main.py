from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import zones

app = FastAPI(
    title="Parking Intelligence API",
    description="API for Parking-Induced Congestion Intelligence System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
