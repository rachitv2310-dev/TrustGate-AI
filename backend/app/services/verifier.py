from typing import List
from backend.app.schemas.claim import Claim, VerificationVerdict
from backend.app.config import settings


class ClaimVerifierService:
    """
    Service responsible for verifying claims against retrieved evidence snippets.
    Produces verdict: SUPPORTED, CONTRADICTED, or INSUFFICIENT.
    Uses configurable model (e.g., gemma3:4b) via settings.
    """

    def __init__(self):
        self.model = settings.VERIFICATION_MODEL

    def verify_claim(self, claim: Claim, evidence: List[str]) -> VerificationVerdict:
        """
        Verify a single claim against evidence passages.
        
        TODO: Implement NLI / LLM stance verification logic using configured model.
        """
        if not evidence:
            return VerificationVerdict.INSUFFICIENT
        
        # Placeholder return
        return VerificationVerdict.SUPPORTED
