from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

# ==========================================
# ENUMS (Strictly following the Problem Statement)
# ==========================================

class EvidenceVerdict(str, Enum):
    consistent = "consistent"
    inconsistent = "inconsistent"
    insufficient_data = "insufficient_data"

class CaseType(str, Enum):
    wrong_transfer = "wrong_transfer"
    payment_failed = "payment_failed"
    refund_request = "refund_request"
    duplicate_payment = "duplicate_payment"
    merchant_settlement_delay = "merchant_settlement_delay"
    agent_cash_in_issue = "agent_cash_in_issue"
    phishing_or_social_engineering = "phishing_or_social_engineering"
    other = "other"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Department(str, Enum):
    customer_support = "customer_support"
    dispute_resolution = "dispute_resolution"
    payments_ops = "payments_ops"
    merchant_operations = "merchant_operations"
    agent_operations = "agent_operations"
    fraud_risk = "fraud_risk"

# ==========================================
# INPUT MODELS (POST /analyze-ticket Request)
# ==========================================

class TransactionEntry(BaseModel):
    transaction_id: str
    timestamp: str
    type: str
    amount: float
    counterparty: str
    status: str

class TicketRequest(BaseModel):
    ticket_id: str
    complaint: str
    language: Optional[str] = None
    channel: Optional[str] = None
    user_type: Optional[str] = None
    campaign_context: Optional[str] = None
    
    # Critical: Default to empty list to prevent NoneType errors if omitted by harness
    transaction_history: Optional[List[TransactionEntry]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# ==========================================
# OUTPUT MODEL (POST /analyze-ticket Response)
# ==========================================

class TicketResponse(BaseModel):
    ticket_id: str
    relevant_transaction_id: Optional[str] = None
    evidence_verdict: EvidenceVerdict
    case_type: CaseType
    severity: Severity
    department: Department
    agent_summary: str
    recommended_next_action: str
    customer_reply: str
    human_review_required: bool
    confidence: Optional[float] = None
    reason_codes: Optional[List[str]] = Field(default_factory=list)

    # ---------------------------------------------------------
    # ENUM COERCION LAYER: Safeguard against LLM Hallucinations
    # ---------------------------------------------------------
    
    @field_validator("evidence_verdict", mode="before")
    def coerce_evidence_verdict(cls, v):
        if v not in [e.value for e in EvidenceVerdict]:
            return EvidenceVerdict.insufficient_data.value
        return v

    @field_validator("case_type", mode="before")
    def coerce_case_type(cls, v):
        if v not in [e.value for e in CaseType]:
            return CaseType.other.value
        return v

    @field_validator("severity", mode="before")
    def coerce_severity(cls, v):
        if v not in [e.value for e in Severity]:
            return Severity.medium.value
        return v

    @field_validator("department", mode="before")
    def coerce_department(cls, v):
        if v not in [e.value for e in Department]:
            return Department.customer_support.value
        return v