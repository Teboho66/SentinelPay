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
        return [
           record for record in self.find_all()
           if getattr(record, "_record_hash", None) != getattr(record, "_expected_hash", None)
    ]

class InMemoryAccountProfileRepository(InMemoryRepository):

    def find_new_accounts(self):
        return [
            profile for profile in self.find_all()
            if getattr(profile, "transaction_count", 0) <= 3
        ]


class InMemoryCustomerDisputeRepository(InMemoryRepository):

    def find_by_id(self, dispute_id):
        for dispute in self.find_all():
            if getattr(dispute, "dispute_id", None) == dispute_id:
                return dispute
        return None

    def find_by_transaction_id(self, transaction_id):
        for dispute in self.find_all():
            if getattr(dispute, "transaction_id", None) == transaction_id:
                return dispute
        return None

    def find_open_disputes(self):
        return [
            dispute for dispute in self.find_all()
            if "OPEN" in str(getattr(dispute, "status", ""))
        ]

    def find_by_status(self, status):
        return [
            dispute for dispute in self.find_all()
            if getattr(dispute, "status", None) == status
        ]

class InMemoryStepUpChallengeRepository(InMemoryRepository):

    def find_by_transaction_id(self, transaction_id):
        for challenge in self.find_all():
            if getattr(challenge, "transaction_id", None) == transaction_id:
                return challenge
        return None

    def find_by_status(self, status):
        return [
            challenge for challenge in self.find_all()
            if getattr(challenge, "status", None) == status
        ]

    def find_expired(self):
        return [
           challenge for challenge in self.find_all()
           if getattr(challenge, "ttl_seconds", 300) <= 0
           and "VERIFIED" not in str(getattr(challenge, "status", ""))
    ]