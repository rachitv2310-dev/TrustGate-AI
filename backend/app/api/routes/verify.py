from fastapi import APIRouter, HTTPException

try:
    from backend.app.schemas.verification import VerificationRequest
    from backend.app.schemas.report import VerificationReport
    from backend.app.services.pipeline import VerificationPipeline
except ImportError:
    from app.schemas.verification import VerificationRequest
    from app.schemas.report import VerificationReport
    from app.services.pipeline import VerificationPipeline

router = APIRouter(prefix="/verify", tags=["Verification"])
pipeline = VerificationPipeline()


@router.post("/", response_model=VerificationReport)
async def verify_response(payload: VerificationRequest) -> VerificationReport:
    """
    Verification API Route executing full LLM answer generation, claim extraction,
    retrieval, and stance verification pipeline.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question text cannot be empty.")

    try:
        report = await pipeline.run(payload)
        return report
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except RuntimeError as run_err:
        raise HTTPException(status_code=500, detail=str(run_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification pipeline failed: {str(exc)}")
