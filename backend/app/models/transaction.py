from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import TransferType


class Transaction(BaseModel):
    id: str = Field(..., description="Unique Decentro transaction ID, e.g. dec_987654321")
    reference_id: str = Field(..., description="Client internal reference ID, e.g. payroll_4821")
    amount: float = Field(..., ge=0.0, description="Transfer amount in fractional units (e.g. 25000.00)")
    currency: str = Field(default="INR", description="Currency code (e.g. INR)")
    transfer_type: TransferType = Field(default=TransferType.IMPS, description="Transfer modality (IMPS, NEFT, RTGS, UPI)")
    beneficiary_id: str = Field(..., description="Beneficiary identifier")
    created_at: datetime = Field(..., description="Transaction creation timestamp (ISO 8601)")
