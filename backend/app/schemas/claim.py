from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class VerificationVerdict(str, Enum):
    """Verdict for factual claim verification against evidence."""
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT = "INSUFFICIENT"


class Claim(BaseModel):
    """
    Simplified atomic claim schema.
    """
    id: Optional[str] = Field(None, description="Unique identifier for the claim")
    text: str = Field(..., description="The atomic claim statement")
    type: Optional[str] = Field("FACTUAL", description="Classification category of the claim")
    importance: Optional[float] = Field(1.0, description="Relative importance score of the claim")
    verifiable: bool = Field(True, description="Whether the claim can be empirically verified")
    verdict: Optional[VerificationVerdict] = Field(None, description="Verification verdict against evidence")
    evidence: List[str] = Field(default_factory=list, description="Supporting or contradicting evidence passages")
