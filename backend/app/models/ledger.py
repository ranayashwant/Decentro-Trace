from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from app.models.enums import LedgerEntryType


class LedgerEntry(BaseModel):
    id: str = Field(..., description="Unique ledger entry ID, e.g. led_deb_001")
    transaction_id: str = Field(..., description="Associated transaction ID")
    entry_type: LedgerEntryType = Field(..., description="DEBIT, REVERSAL, or CREDIT")
    amount: float = Field(..., ge=0.0, description="Amount moved in this ledger entry")
    currency: str = Field(default="INR", description="Currency code")
    occurred_at: datetime = Field(..., description="Timestamp of book entry")
    reference_id: str = Field(..., description="Associated business reference ID")
    payload: dict[str, Any] = Field(default_factory=dict, description="Metadata or account specifics")
