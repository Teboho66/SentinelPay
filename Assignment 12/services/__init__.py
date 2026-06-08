from .exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    BusinessRuleViolationError,
    InvalidStateTransitionError,
    PromotionGateFailedError,
)


def __getattr__(name):
    if name == "TransactionService":
        from mapping.transaction_service import TransactionService

        return TransactionService

    if name == "FraudCaseService":
        from mapping.fraud_case_service import FraudCaseService

        return FraudCaseService

    if name == "MLModelService":
        from mapping.ml_model_service import MLModelService

        return MLModelService

    raise AttributeError(f"module 'services' has no attribute {name!r}")


__all__ = [
    "TransactionService",
    "FraudCaseService",
    "MLModelService",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "BusinessRuleViolationError",
    "InvalidStateTransitionError",
    "PromotionGateFailedError",
]
