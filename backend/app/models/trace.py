from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.enums import TransactionStatus, FailureStage
from app.models.transaction import Transaction
from app.models.event import Event


class LifecycleTransition(BaseModel):
    from_status: Optional[TransactionStatus] = None
    to_status: TransactionStatus
    event_id: str
    event_type: str
    occurred_at: datetime


class LifecycleAnalysis(BaseModel):
    initial_status: Optional[TransactionStatus] = None
    final_status: TransactionStatus
    is_terminal: bool
    duration_ms: Optional[int] = None
    transitions: list[LifecycleTransition] = Field(default_factory=list)


class FailureAnalysis(BaseModel):
    failed: bool
    failure_stage: FailureStage
    observed_status: Optional[TransactionStatus] = None
    observed_error_code: Optional[str] = None
    observed_error_message: Optional[str] = None
    failure_event_id: Optional[str] = None
    failure_timestamp: Optional[datetime] = None


class StateConflict(BaseModel):
    event_1_id: str
    event_1_type: str
    event_1_status: TransactionStatus
    event_2_id: str
    event_2_type: str
    event_2_status: TransactionStatus
    description: str


class TraceIntegrity(BaseModel):
    total_events_received: int
    canonical_events_count: int
    duplicate_events_count: int
    out_of_order_received: bool
    missing_expected_events: list[str] = Field(default_factory=list)
    state_conflicts: list[StateConflict] = Field(default_factory=list)
    is_clean: bool


class ReconciliationResult(BaseModel):
    debited_amount: float
    reversed_amount: float
    credited_amount: float
    net_impact: float
    currency: str = "INR"
    reconciled: bool
    entries_count: int


class Trace(BaseModel):
    transaction: Transaction
    canonical_events: list[Event]
    duplicate_events: list[Event] = Field(default_factory=list)
    lifecycle: LifecycleAnalysis
    failure_analysis: FailureAnalysis
    integrity: TraceIntegrity
    reconciliation: ReconciliationResult
