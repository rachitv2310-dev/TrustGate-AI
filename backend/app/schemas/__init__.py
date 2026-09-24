try:
    from backend.app.schemas.claim import Claim, VerificationVerdict
    from backend.app.schemas.verification import VerificationRequest, VerificationResult
    from backend.app.schemas.report import VerificationReport
except ImportError:
    from app.schemas.claim import Claim, VerificationVerdict
    from app.schemas.verification import VerificationRequest, VerificationResult
    from app.schemas.report import VerificationReport

__all__ = [
    "Claim",
    "VerificationVerdict",
    "VerificationRequest",
    "VerificationResult",
    "VerificationReport"
]
