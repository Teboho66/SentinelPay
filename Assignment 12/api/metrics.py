"""
SentinelPay – Assignment 12
api/metrics.py

Prometheus metrics module.
Exposes custom counters for observability:
  - sentinelpay_transactions_total: number of transactions submitted
  - sentinelpay_fraud_decisions_total: fraud decisions made (labelled by decision type)
  - sentinelpay_fraud_cases_total: fraud cases created
"""

from prometheus_client import Counter

# ── Transaction counter ────────────────────────────────────────────────────────
transactions_total = Counter(
    "sentinelpay_transactions_total",
    "Total number of transactions submitted",
    labelnames=["channel"],
)

# ── Fraud decision counter ─────────────────────────────────────────────────────
fraud_decisions_total = Counter(
    "sentinelpay_fraud_decisions_total",
    "Total number of fraud decisions made, labelled by decision type",
    labelnames=["decision_type"],
)

# ── Fraud case counter ─────────────────────────────────────────────────────────
fraud_cases_total = Counter(
    "sentinelpay_fraud_cases_total",
    "Total number of fraud cases created",
)
