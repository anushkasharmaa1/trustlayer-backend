"""
main.py
-------
FastAPI application factory.

Registers:
  - Lifespan hooks (DB connect / disconnect)
  - All route modules
  - Global exception handlers
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import startup_db, shutdown_db
from routes import transactions, scoring, simulation

settings = get_settings()


# ---------------------------------------------------------------------------
# Lifespan: runs startup/shutdown logic around the app's lifetime
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db()
    yield
    await shutdown_db()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Behavioral credit scoring infrastructure for gig economy workers. "
        "Computes a Trust Score (0-1000) from UPI/digital transaction behavior."
    ),
    lifespan=lifespan,
)

# --- Route registration ---
app.include_router(transactions.router, tags=["Transactions"])
app.include_router(scoring.router,      tags=["Scoring"])
app.include_router(simulation.router,   tags=["Simulation"])


# ---------------------------------------------------------------------------
# Global exception handler — always return structured JSON
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error.", "detail": str(exc)},
    )


# ---------------------------------------------------------------------------
# Health check (no auth required)
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Meta"])
async def health():
    """Quick liveness probe — returns app name and version."""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
