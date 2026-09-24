import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from backend.app.schemas.claim import Claim, VerificationVerdict
    from backend.app.services.trust_score import TrustScoreCalculatorService
except ImportError:
    from app.schemas.claim import Claim, VerificationVerdict
    from app.services.trust_score import TrustScoreCalculatorService


class TestTrustScoreCalculator(unittest.TestCase):
    """
    Unit test suite for TrustScoreCalculatorService verifying V1 Trust Score and Hallucination Percentage calculation.
    """

    def setUp(self):
        self.calculator = TrustScoreCalculatorService()

    def test_case_a_supported_supported(self):
        """Case A: SUPPORTED, SUPPORTED -> Trust Score = 100, Hallucination = 0"""
        claims = [
            Claim(id="c1", text="Claim 1", verifiable=True, verdict=VerificationVerdict.SUPPORTED),
            Claim(id="c2", text="Claim 2", verifiable=True, verdict=VerificationVerdict.SUPPORTED),
        ]
        score = self.calculator.calculate_score(claims)
        hallucination = self.calculator.calculate_hallucination_percentage(claims)

        self.assertEqual(score, 100.0)
        self.assertEqual(hallucination, 0.0)

    def test_case_b_supported_contradicted(self):
        """Case B: SUPPORTED, CONTRADICTED -> Trust Score = 50, Hallucination = 50"""
        claims = [
            Claim(id="c1", text="Claim 1", verifiable=True, verdict=VerificationVerdict.SUPPORTED),
            Claim(id="c2", text="Claim 2", verifiable=True, verdict=VerificationVerdict.CONTRADICTED),
        ]
        score = self.calculator.calculate_score(claims)
        hallucination = self.calculator.calculate_hallucination_percentage(claims)

        self.assertEqual(score, 50.0)
        self.assertEqual(hallucination, 50.0)

    def test_case_c_supported_insufficient(self):
        """Case C: SUPPORTED, INSUFFICIENT -> Trust Score = 75, Hallucination = 0"""
        claims = [
            Claim(id="c1", text="Claim 1", verifiable=True, verdict=VerificationVerdict.SUPPORTED),
            Claim(id="c2", text="Claim 2", verifiable=True, verdict=VerificationVerdict.INSUFFICIENT),
        ]
        score = self.calculator.calculate_score(claims)
        hallucination = self.calculator.calculate_hallucination_percentage(claims)

        self.assertEqual(score, 75.0)
        self.assertEqual(hallucination, 0.0)

    def test_case_d_supported_contradicted_insufficient(self):
        """Case D: SUPPORTED, CONTRADICTED, INSUFFICIENT -> Trust Score = 50, Hallucination = 33.33"""
        claims = [
            Claim(id="c1", text="Claim 1", verifiable=True, verdict=VerificationVerdict.SUPPORTED),
            Claim(id="c2", text="Claim 2", verifiable=True, verdict=VerificationVerdict.CONTRADICTED),
            Claim(id="c3", text="Claim 3", verifiable=True, verdict=VerificationVerdict.INSUFFICIENT),
        ]
        score = self.calculator.calculate_score(claims)
        hallucination = self.calculator.calculate_hallucination_percentage(claims)

        self.assertEqual(score, 50.0)
        self.assertAlmostEqual(hallucination, 33.33, places=2)

    def test_case_e_no_verifiable_claims(self):
        """Case E: No verifiable claims -> Trust Score = 0, Hallucination = 0"""
        claims_unverifiable = [
            Claim(id="c1", text="Opinion 1", verifiable=False, verdict=VerificationVerdict.INSUFFICIENT),
        ]
        score_unverifiable = self.calculator.calculate_score(claims_unverifiable)
        hallucination_unverifiable = self.calculator.calculate_hallucination_percentage(claims_unverifiable)

        self.assertEqual(score_unverifiable, 0.0)
        self.assertEqual(hallucination_unverifiable, 0.0)

        score_empty = self.calculator.calculate_score([])
        hallucination_empty = self.calculator.calculate_hallucination_percentage([])

        self.assertEqual(score_empty, 0.0)
        self.assertEqual(hallucination_empty, 0.0)


if __name__ == "__main__":
    unittest.main()
