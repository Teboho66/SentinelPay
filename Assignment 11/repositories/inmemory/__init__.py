from .base_inmemory import InMemoryRepository


class InMemoryTransactionRepository(InMemoryRepository):

    def find_by_account_id_token(self, account_id_token):
        return [
            txn for txn in self.find_all()
            if getattr(txn, "account_id_token", None) == account_id_token
        ]

    def find_by_decision(self, decision):
        return [
            txn for txn in self.find_all()
            if getattr(txn, "decision", None) == decision
        ]

    def find_by_risk_tier(self, risk_tier):
        return [
            txn for txn in self.find_all()
            if getattr(txn, "risk_tier", None) == risk_tier
        ]

    def find_flagged(self):
        return [
            txn for txn in self.find_all()
            if getattr(txn, "decision", None) == "HARD_BLOCK"
        ]


class InMemoryFraudCaseRepository(InMemoryRepository):

    def find_by_transaction_id(self, transaction_id):
        for case in self.find_all():
            if getattr(case, "transaction_id", None) == transaction_id:
                return case
        return None

    def find_by_account_id_token(self, account_id_token):
        return [
            case for case in self.find_all()
            if getattr(case, "account_id_token", None) == account_id_token
        ]

    def find_by_risk_tier(self, risk_tier):
        return [
            case for case in self.find_all()
            if getattr(case, "risk_tier", None) == risk_tier
        ]
    def find_by_priority(self, priority):
        return [
            case for case in self.find_all()
            if getattr(case, "priority", None) == priority
    ]
    def find_by_status(self, status):
        return [
            case for case in self.find_all()
            if getattr(case, "status", None) == status
        ]
    def find_open_cases(self):
        return [
            case for case in self.find_all()
            if getattr(case, "status", None) in (
                "OPEN",
                "IN_REVIEW",
        )
    ]
    def find_by_analyst_id(self, analyst_id):
       return [
            case for case in self.find_all()
            if getattr(case, "analyst_id", None) == analyst_id
    ]

class InMemoryMLModelRepository(InMemoryRepository):

    def find_production_models(self):
        return [
            model for model in self.find_all()
            if getattr(model, "stage", None) == "PRODUCTION"
        ]

    def find_by_model_name(self, model_name):
        return [
            model for model in self.find_all()
            if getattr(model, "model_name", None) == model_name
        ]

    def find_by_stage(self, stage):
        return [
            model for model in self.find_all()
            if getattr(model, "stage", None) == stage
        ]

    def find_by_name_and_stage(self, model_name, stage):
        for model in self.find_all():
          if (
              getattr(model, "model_name", None) == model_name
              and getattr(model, "stage", None) == stage
          ):
           return model
        return None


class InMemoryAuditRecordRepository(InMemoryRepository):

    def find_by_transaction_id(self, transaction_id):
        for record in self.find_all():
            if getattr(record, "transaction_id", None) == transaction_id:
                return record
        return None

    def find_by_decision(self, decision):
        return [
            record for record in self.find_all()
            if getattr(record, "decision", None) == decision
        ]

    def delete(self, entity_id):
        raise RuntimeError(
            "BR-AR2: Audit records are immutable and cannot be deleted"
        )

    def find_tampered(self, signing_key):
        return []


class InMemoryAccountProfileRepository(InMemoryRepository):
    pass


class InMemoryCustomerDisputeRepository(InMemoryRepository):
    pass


class InMemoryStepUpChallengeRepository(InMemoryRepository):
    pass