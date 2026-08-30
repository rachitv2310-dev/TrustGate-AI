from typing import Optional
from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    """Schema for verification request input."""
    question: str = Field(..., description="Original user prompt or legal query")
    response: str = Field(..., description="AI-generated response text to be verified")


class VerificationResult(BaseModel):
    """Placeholder schema for internal verification result state."""
    success: bool = True
    message: Optional[str] = None
