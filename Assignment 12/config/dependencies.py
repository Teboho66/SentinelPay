"""
SentinelPay – Assignment 12
api/dependencies.py

FastAPI dependency injection.
Services and repositories are created once per application lifetime
(application-scoped singletons) using FastAPI's dependency system.
Switching storage backend (MEMORY → DATABASE) requires changing only
this file — all route handlers are untouched.
"""

from __future__ import annotations
import sys
import os

for _p in ("../Assignment10", "../Assignment11"):
    _abs = os.path.abspath(os.path.join(os.path.dirname(__file__), _p))
    if _abs not in sys.path:
        sys.path.insert(0, _abs)

from repositories.inmemory import (
    InMemoryTransactionRepository,
    InMemoryFraudCaseRepository,
    InMemoryMLModelRepository,
)
from mapping.transaction_service import TransactionService
from mapping.fraud_case_service import FraudCaseService
from mapping.ml_model_service import MLModelService

# ── Application-scoped repository singletons ──────────────────────────────────
# In production these would be backed by PostgreSQL / Redis connections.
# Switching requires only replacing the constructor here.

_transaction_repo = InMemoryTransactionRepository()
_fraud_case_repo = InMemoryFraudCaseRepository()
_ml_model_repo = InMemoryMLModelRepository()

# ── Service factories (injected into route handlers via FastAPI Depends) ──────


def get_transaction_service() -> TransactionService:
    return TransactionService(_transaction_repo)


def get_fraud_case_service() -> FraudCaseService:
    return FraudCaseService(_fraud_case_repo)


def get_ml_model_service() -> MLModelService:
    return MLModelService(_ml_model_repo)
