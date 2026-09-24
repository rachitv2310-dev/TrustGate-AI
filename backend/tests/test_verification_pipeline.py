import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from backend.app.schemas.verification import VerificationRequest
    from backend.app.schemas.report import VerificationReport
    from backend.app.schemas.claim import Claim, VerificationVerdict
    from backend.app.services.pipeline import VerificationPipeline
    from backend.app.services.verifier import ClaimVerifierService
except ImportError:
    from app.schemas.verification import VerificationRequest
    from app.schemas.report import VerificationReport
    from app.schemas.claim import Claim, VerificationVerdict
    from app.services.pipeline import VerificationPipeline
    from app.services.verifier import ClaimVerifierService


class TestVerificationPipeline(unittest.IsolatedAsyncioTestCase):
    """
    Unit test suite for the verification pipeline and Ollama LLM integrations.
    Mocks local Ollama calls to ensure deterministic unit testing.
    """

    def setUp(self):
        self.mock_ollama = MagicMock()
        self.mock_extractor = MagicMock()
        self.mock_retriever = MagicMock()
        self.mock_verifier = MagicMock()

        self.pipeline = VerificationPipeline(
            ollama_service=self.mock_ollama,
            claim_extractor=self.mock_extractor,
            retriever=self.mock_retriever,
            verifier=self.mock_verifier,
        )

    async def test_01_question_only_generation_path(self):
        """TEST 1: Question-only request invokes hf.co/GSMS-B/Indian-Legal-Llama-3.2-3B-GGUF:latest to generate AI response."""
        self.mock_ollama.generate.return_value = {
            "model": "hf.co/GSMS-B/Indian-Legal-Llama-3.2-3B-GGUF:latest",
            "response": "Under BNS Section 303, the punishment for theft is imprisonment up to 3 years."
        }
        self.mock_extractor.extract_claims.return_value = [
            Claim(id="claim-1", text="Under BNS Section 303, punishment for theft is imprisonment up to 3 years.", type="FACTUAL")
        ]
        self.mock_retriever.retrieve.return_value = [
            {"evidence_text": "303. Theft. Whoever commits theft shall be punished with imprisonment up to three years."}
        ]
        self.mock_verifier.verify_claim.return_value = VerificationVerdict.SUPPORTED

        req = VerificationRequest(question="What is the punishment for theft?")
        report = await self.pipeline.run(req)

        # Verify hf.co/GSMS-B/Indian-Legal-Llama-3.2-3B-GGUF:latest was called for generation
        self.mock_ollama.generate.assert_called_once()
        call_kwargs = self.mock_ollama.generate.call_args[1]
        self.assertEqual(call_kwargs.get("model"), "hf.co/GSMS-B/Indian-Legal-Llama-3.2-3B-GGUF:latest")

        # Verify report structure
        self.assertEqual(report.question, "What is the punishment for theft?")
        self.assertIn("Section 303", report.response)
        self.assertEqual(len(report.claims), 1)
        self.assertEqual(report.claims[0].verdict, VerificationVerdict.SUPPORTED)

    async def test_02_provided_response_path(self):
        """TEST 2: Request with provided response skips hf.co/GSMS-B/Indian-Legal-Llama-3.2-3B-GGUF:latest generation."""
        self.mock_extractor.extract_claims.return_value = [
            Claim(id="claim-1", text="Section 103 defines punishment for murder.", type="FACTUAL")
        ]
        self.mock_retriever.retrieve.return_value = [
            {"evidence_text": "103. Punishment for murder. Whoever commits murder shall be punished with death or imprisonment for life."}
        ]
        self.mock_verifier.verify_claim.return_value = VerificationVerdict.SUPPORTED

        req = VerificationRequest(
            question="What is murder?",
            response="Section 103 defines punishment for murder."
        )
        report = await self.pipeline.run(req)

        # Verify hf.co/GSMS-B/Indian-Legal-Llama-3.2-3B-GGUF:latest was NOT called
        self.mock_ollama.generate.assert_not_called()
        self.assertEqual(report.response, "Section 103 defines punishment for murder.")
        self.assertEqual(len(report.claims), 1)

    async def test_03_gemma_verdict_parsing_supported(self):
        """TEST 3: Gemma verifier parses SUPPORTED output accurately."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.return_value = {
            "model": "gemma3:4b",
            "response": "The claim is fully SUPPORTED by the provided evidence passage."
        }
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c1", text="Theft is punished under Section 303.")
        verdict = verifier.verify_claim(claim, ["Section 303 punishes theft."])

        self.assertEqual(verdict, VerificationVerdict.SUPPORTED)

    async def test_04_gemma_verdict_parsing_contradicted(self):
        """TEST 4: Gemma verifier parses CONTRADICTED output accurately."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.return_value = {
            "model": "gemma3:4b",
            "response": "VERDICT: CONTRADICTED. Section 103 deals with murder, not theft."
        }
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c1", text="Section 103 defines theft.")
        verdict = verifier.verify_claim(claim, ["103. Punishment for murder."])

        self.assertEqual(verdict, VerificationVerdict.CONTRADICTED)

    async def test_05_gemma_verdict_parsing_insufficient(self):
        """TEST 5: Gemma verifier parses INSUFFICIENT output accurately."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.return_value = {
            "model": "gemma3:4b",
            "response": "VERDICT: INSUFFICIENT. The text does not mention penalty details."
        }
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c1", text="Penalty includes community service.")
        verdict = verifier.verify_claim(claim, ["103. Punishment for murder."])

        self.assertEqual(verdict, VerificationVerdict.INSUFFICIENT)

    async def test_06_empty_evidence_path(self):
        """TEST 6: Claim with empty evidence returns INSUFFICIENT without calling Gemma."""
        mock_ollama_gemma = MagicMock()
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c1", text="Some random unevidenced claim.")
        verdict = verifier.verify_claim(claim, [])

        self.assertEqual(verdict, VerificationVerdict.INSUFFICIENT)
        mock_ollama_gemma.generate.assert_not_called()

    async def test_07_ollama_failure_safety(self):
        """TEST 7: Ollama failure or exception returns INSUFFICIENT (never SUPPORTED)."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.side_effect = RuntimeError("Ollama connection timeout")
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c1", text="Theft punishment section.")
        verdict = verifier.verify_claim(claim, ["Valid evidence passage."])

        self.assertNotEqual(verdict, VerificationVerdict.SUPPORTED)
        self.assertEqual(verdict, VerificationVerdict.INSUFFICIENT)

    async def test_08_unsupported_additional_qualifier_is_insufficient(self):
        """TEST 8: Unsupported additional qualifier e.g. governor approval yields INSUFFICIENT."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.return_value = {
            "model": "gemma3:4b",
            "response": "VERDICT: INSUFFICIENT"
        }
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c8", text="Murder under Section 101 of BNS requires approval from a state governor before prosecution.")
        evidence = [{"section_number": "101", "evidence_text": "101. Murder.—Except in the cases hereinafter excepted, culpable homicide is murder, if the act by which the death is caused is done with the intention of causing death."}]
        verdict = verifier.verify_claim(claim, evidence)
        self.assertEqual(verdict, VerificationVerdict.INSUFFICIENT)

    async def test_09_direct_conflicting_statement_is_contradicted(self):
        """TEST 9: Directly conflicting section or statement yields CONTRADICTED."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.return_value = {
            "model": "gemma3:4b",
            "response": "VERDICT: CONTRADICTED"
        }
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c9", text="Robbery is defined under Section 304 of the Bharatiya Nyaya Sanhita, 2023.")
        evidence = [{"section_number": "309", "title": "Robbery", "evidence_text": "309. Robbery.—In all robbery there is either theft or extortion."}]
        verdict = verifier.verify_claim(claim, evidence)
        self.assertEqual(verdict, VerificationVerdict.CONTRADICTED)

    async def test_10_directly_supported_claim_is_supported(self):
        """TEST 10: Directly supported statement yields SUPPORTED."""
        mock_ollama_gemma = MagicMock()
        mock_ollama_gemma.generate.return_value = {
            "model": "gemma3:4b",
            "response": "VERDICT: SUPPORTED"
        }
        verifier = ClaimVerifierService(ollama_service=mock_ollama_gemma)
        claim = Claim(id="c10", text="Cheating is defined under Section 318 of the Bharatiya Nyaya Sanhita 2023.")
        evidence = [{"section_number": "318", "title": "Cheating", "evidence_text": "318. Cheating.—(1) Whoever, by deceiving any person..."}]
        verdict = verifier.verify_claim(claim, evidence)
        self.assertEqual(verdict, VerificationVerdict.SUPPORTED)


if __name__ == "__main__":
    unittest.main()
