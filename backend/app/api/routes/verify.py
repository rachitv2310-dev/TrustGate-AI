from fastapi import APIRouter, HTTPException
from backend.app.schemas.verification import VerificationRequest
from backend.app.schemas.report import VerificationReport
from backend.app.schemas.claim import Claim, VerificationVerdict

router = APIRouter(prefix="/verify", tags=["Verification"])


@router.post("/", response_model=VerificationReport)
async def verify_response(payload: VerificationRequest) -> VerificationReport:
    """
    Verification API Route (Placeholder).
    
    Workflow Roadmap:
    Input → Claim Extraction → Retrieval → Verification → Trust Score → Final Report
    """
    if not payload.question.strip() or not payload.response.strip():
        raise HTTPException(status_code=400, detail="Question and Response text cannot be empty.")

    placeholder_claims = [
        Claim(
            id="claim-1",
            text="Sample atomic claim statement.",
            type="FACTUAL",
            importance=1.0,
            verifiable=True,
            verdict=VerificationVerdict.SUPPORTED,
            evidence=["Sample evidence snippet."]
        )
    ]

    return VerificationReport(
        question=payload.question,
        response=payload.response,
        claims=placeholder_claims,
        trust_score=0.0,
        status="PENDING"
    )
