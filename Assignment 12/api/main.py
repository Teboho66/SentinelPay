"""
SentinelPay – Assignment 12
api/main.py

FastAPI application entry point.
OpenAPI docs auto-generated at:
  /docs   → Swagger UI
  /redoc  → ReDoc
  /openapi.json → raw OpenAPI JSON
"""

from __future__ import annotations
import sys
import os

for _p in ("../Assignment10", "../Assignment11", "."):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from handlers.routes.transactions import router as transactions_router
from handlers.routes.fraud_cases import router as fraud_cases_router
from handlers.routes.ml_models import router as ml_models_router

app = FastAPI(
    title="SentinelPay Fraud Detection API",
    description=(
        "Real-time fraud detection and prevention REST API. "
        "Implements the Transaction ingestion pipeline (FR-01–FR-08), "
        "Fraud Case management (FR-09–FR-10), and ML Model lifecycle (FR-13–FR-14) "
        "from the SentinelPay System Requirements Document.\n\n"
        "**Author:** Teboho Mokoni  \n"
        "**Assignment:** 12 – Service Layer and REST API  \n"
        "**Stack:** Python 3.12 · FastAPI · In-memory repositories (A11)"
    ),
    version="1.0.0",
    contact={"name": "Teboho Mokoni", "url": "https://github.com/Teboho66/SentinelPay"},
    license_info={"name": "Academic project — CPUT Postgraduate Diploma"},
    openapi_tags=[
        {
            "name": "Transactions",
            "description": (
                "Submit transactions, apply ML ensemble fraud decisions, "
                "and query the transaction store. Maps to FR-01 through FR-08."
            ),
        },
        {
            "name": "Fraud Cases",
            "description": (
                "Manage fraud investigation cases. Create cases for HARD_BLOCK "
                "transactions, assign to analysts, resolve with CONFIRMED/DISMISSED. "
                "Maps to FR-09 and FR-10."
            ),
        },
        {
            "name": "ML Models",
            "description": (
                "Register, evaluate, and promote ML model versions through the "
                "TRAINING → STAGING → PRODUCTION lifecycle. Hot-swap artifacts "
                "without service restart. Maps to FR-13 and FR-14."
            ),
        },
    ],
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(transactions_router)
app.include_router(fraud_cases_router)
app.include_router(ml_models_router)


# ── Prometheus instrumentation ─────────────────────────────────────────────────
Instrumentator().instrument(app).expose(app)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="API health check")
def health_check():
    """Returns 200 OK when the API is running."""
    return {
        "status": "healthy",
        "service": "SentinelPay Fraud Detection API",
        "version": "1.0.0",
    }


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({"message": "SentinelPay API. Visit /docs for Swagger UI."})