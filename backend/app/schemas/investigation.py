from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceItem(BaseModel):
    event_id: str = Field(..., description="ID of the event providing factual proof")
    reason: str = Field(..., description="Why this event serves as evidence for the conclusion")


class InvestigationResult(BaseModel):
    summary: str = Field(..., description="High-level technical summary of transaction lifecycle")
    failure_stage: Optional[str] = Field(None, description="Stage at which failure occurred, if applicable")
    root_cause: str = Field(..., description="Evidence-based root cause explanation")
    evidence: list[EvidenceItem] = Field(default_factory=list, description="Specific event references supporting the analysis")
    recommended_action: str = Field(..., description="Actionable recommendation for engineers/ops")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH, description="Confidence in interpretation based on data sufficiency")
    uncertainty: Optional[str] = Field(None, description="Gaps, missing data, or conflicts that limit certainty")
