"""
SentinelPay – Assignment 12
services/exceptions.py

Domain exceptions raised by the service layer.
These are mapped to HTTP status codes in the API layer.
"""


class EntityNotFoundError(Exception):
    """Raised when an entity cannot be found by ID (→ HTTP 404)."""
    def __init__(self, entity: str, entity_id: str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} '{entity_id}' not found.")


class DuplicateEntityError(Exception):
    """Raised when a unique constraint would be violated (→ HTTP 409)."""
    def __init__(self, entity: str, key: str, value: str):
        super().__init__(f"{entity} with {key}='{value}' already exists.")


class BusinessRuleViolationError(Exception):
    """Raised when a SentinelPay business rule is violated (→ HTTP 422)."""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        super().__init__(f"[{rule}] {message}")


class InvalidStateTransitionError(Exception):
    """Raised when an operation is invalid for the entity's current state (→ HTTP 409)."""
    def __init__(self, entity: str, current_state: str, attempted_operation: str):
        super().__init__(
            f"{entity} in state '{current_state}' cannot perform '{attempted_operation}'."
        )


class PromotionGateFailedError(Exception):
    """Raised when an MLModel fails the precision/recall promotion gate (→ HTTP 422)."""
    def __init__(self, model_id: str, precision: float, recall: float):
        super().__init__(
            f"Model '{model_id}' failed promotion gate: "
            f"precision={precision:.2f} (need ≥0.85), recall={recall:.2f} (need ≥0.80). "
            f"Both thresholds must be met simultaneously (BR-ML1)."
        )