from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.enums import EventType, EventSource, TransactionStatus


class Event(BaseModel):
    id: str = Field(..., description="Unique event identifier, e.g. evt_init_001")
    transaction_id: str = Field(..., description="Associated transaction ID")
    event_type: EventType = Field(..., description="Canonical event type")
    source: EventSource = Field(..., description="Source system emitting this event")
    status: TransactionStatus = Field(..., description="Observed transaction status at event time")
    occurred_at: datetime = Field(..., description="Business/causal occurrence timestamp")
    received_at: datetime = Field(..., description="Ingestion timestamp at gateway")
    correlation_id: Optional[str] = Field(None, description="Downstream or upstream correlation/RRN/UTR ID")
    sequence: int = Field(default=0, description="Sequential ordering hint")
    payload: dict[str, Any] = Field(default_factory=dict, description="Raw event payload")
