"""
conftest.py — pytest configuration for Assignment 11.
Adds the Assignment 10 src directory to sys.path so all tests can import
the SentinelPay domain models (Transaction, FraudCase, MLModel, etc.)
without duplicating them.
"""

import sys
import os

# Resolve the path to Assignment 10's src from the Assignment 11 root
A10_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Assignment10"))
if A10_SRC not in sys.path:
    sys.path.insert(0, A10_SRC)
