from typing import List
try:
    from backend.app.schemas.claim import Claim, VerificationVerdict
except ImportError:
    from app.schemas.claim import Claim, VerificationVerdict


class TrustScoreCalculatorService:
    """
    Service responsible for calculating claim-level and overall trust scores and hallucination percentages.
    TrustGate V1 Claim-Level Trust Calculation Engine.

    Rules for V1:
    - Only claims where claim.verifiable is True are considered.
    - Claim verdicts map to individual scores:
        * SUPPORTED    -> 100.0
        * INSUFFICIENT -> 50.0
        * CONTRADICTED -> 0.0
    - Trust Score = sum(individual verifiable claim scores) / total verifiable claims (range: 0.0 to 100.0).
    - Hallucination % = (count of CONTRADICTED verifiable claims / total verifiable claims) * 100.0 (range: 0.0 to 100.0).
    - If there are zero verifiable claims, both Trust Score and Hallucination % default to 0.0.
    """

    def calculate_score(self, claims: List[Claim]) -> float:
        """
        Calculate overall 0-100 Trust Score based on verifiable claims.
        """
        if not claims:
            return 0.0

        verifiable_claims = [c for c in claims if getattr(c, "verifiable", False)]
        if not verifiable_claims:
            return 0.0

        total_score = 0.0
        for c in verifiable_claims:
            verdict = getattr(c, "verdict", None)
            if verdict == VerificationVerdict.SUPPORTED or verdict == "SUPPORTED":
                total_score += 100.0
            elif verdict == VerificationVerdict.INSUFFICIENT or verdict == "INSUFFICIENT":
                total_score += 50.0
            elif verdict == VerificationVerdict.CONTRADICTED or verdict == "CONTRADICTED":
                total_score += 0.0
            else:
                total_score += 0.0

        score = total_score / len(verifiable_claims)
        return float(min(max(round(score, 2), 0.0), 100.0))

    def calculate_hallucination_percentage(self, claims: List[Claim]) -> float:
        """
        Calculate Hallucination Percentage (percentage of verifiable claims that are CONTRADICTED).
        """
        if not claims:
            return 0.0

        verifiable_claims = [c for c in claims if getattr(c, "verifiable", False)]
        if not verifiable_claims:
            return 0.0

        contradicted_count = 0
        for c in verifiable_claims:
            verdict = getattr(c, "verdict", None)
            if verdict == VerificationVerdict.CONTRADICTED or verdict == "CONTRADICTED":
                contradicted_count += 1

        pct = (contradicted_count / len(verifiable_claims)) * 100.0
        return float(min(max(round(pct, 2), 0.0), 100.0))
