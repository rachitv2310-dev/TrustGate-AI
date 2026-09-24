from typing import List
from pydantic import BaseModel, Field
try:
    from backend.app.schemas.claim import Claim
except ImportError:
    from app.schemas.claim import Claim


class VerificationReport(BaseModel):
    """Schema for final claim-level verification report output."""
    question: str = Field(..., description="Original user prompt or legal query")
    response: str = Field(..., description="AI-generated response text")
    claims: List[Claim] = Field(default_factory=list, description="List of extracted and verified claims")
    trust_score: float = Field(0.0, ge=0.0, le=100.0, description="Calculated overall trust score percentage")
    hallucination_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Calculated hallucination percentage")
    status: str = Field("PENDING", description="Overall verification processing status")
