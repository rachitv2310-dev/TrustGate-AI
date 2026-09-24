import logging
from typing import Optional

try:
    from backend.app.config import settings
    from backend.app.schemas.verification import VerificationRequest
    from backend.app.schemas.report import VerificationReport
    from backend.app.schemas.claim import Claim, VerificationVerdict
    from backend.app.services.llm_service import OllamaService
    from backend.app.services.claim_extractor import ClaimExtractorService
    from backend.app.services.retriever import EvidenceRetrieverService
    from backend.app.services.verifier import ClaimVerifierService
    from backend.app.services.trust_score import TrustScoreCalculatorService
    from backend.services.claim_classification_service import classify_claim
except ImportError:
    from app.config import settings
    from app.schemas.verification import VerificationRequest
    from app.schemas.report import VerificationReport
    from app.schemas.claim import Claim, VerificationVerdict
    from app.services.llm_service import OllamaService
    from app.services.claim_extractor import ClaimExtractorService
    from app.services.retriever import EvidenceRetrieverService
    from app.services.verifier import ClaimVerifierService
    from app.services.trust_score import TrustScoreCalculatorService
    from services.claim_classification_service import classify_claim

logger = logging.getLogger(__name__)


class VerificationPipeline:
    """
    Orchestrator pipeline for claim-level verification workflow.
    Executes:
      User Question -> Answer Generation (qwen2.5:7b via settings.GENERATION_MODEL)
      -> Atomic Claim Extraction (qwen2.5:3b) -> Claim Classification
      -> Hybrid Evidence Retrieval & Reranking -> Stance Verification (gemma3:4b)
      -> Trust Score Calculation -> VerificationReport.
    """

    def __init__(
        self,
        ollama_service: Optional[OllamaService] = None,
        claim_extractor: Optional[ClaimExtractorService] = None,
        retriever: Optional[EvidenceRetrieverService] = None,
        verifier: Optional[ClaimVerifierService] = None,
        trust_calculator: Optional[TrustScoreCalculatorService] = None,
    ):
        self.ollama_service = ollama_service or OllamaService()
        self.claim_extractor = claim_extractor or ClaimExtractorService()
        self.retriever = retriever or EvidenceRetrieverService()
        self.verifier = verifier or ClaimVerifierService()
        self.trust_calculator = trust_calculator or TrustScoreCalculatorService()
        self.generation_model = getattr(settings, "GENERATION_MODEL", "qwen2.5:7b")

    async def run(self, payload: VerificationRequest) -> VerificationReport:
        """
        Execute full verification pipeline.
        """
        question = payload.question.strip() if payload.question else ""
        if not question:
            raise ValueError("Question text cannot be empty.")

        # Step 1: Answer Generation using settings.GENERATION_MODEL (FIX 15)
        if payload.response and payload.response.strip():
            response_text = payload.response.strip()
            logger.info("Using user-provided response text for verification.")
        else:
            logger.info(f"Generating response for question using {self.generation_model}...")
            gen_prompt = f"""You are an authoritative legal AI assistant specializing in Indian law (including Bharatiya Nyaya Sanhita, 2023).
Answer the user's legal question accurately, concisely, and clearly. Do not fabricate section numbers or laws. If uncertain, state your uncertainty clearly.

Question: {question}
Answer:"""
            gen_result = self.ollama_service.generate(
                prompt=gen_prompt,
                model=self.generation_model,
                options={"temperature": 0.3, "num_predict": 512},
                keep_alive="5m",
                timeout=180
            )
            response_text = gen_result.get("response", "").strip()

            if not response_text:
                logger.error(f"Failed to generate response using {self.generation_model}")
                raise RuntimeError(f"Failed to generate AI response from {self.generation_model} model.")

        # Step 2: Atomic Claim Extraction (qwen2.5:3b)
        logger.info("Extracting atomic claims using ClaimExtractorService...")
        claims = self.claim_extractor.extract_claims(response_text)

        # Step 3: Claim Classification & Evidence Retrieval (Phase 1)
        claim_evidence_items_map = {}
        processed_claims = []

        for claim in claims:
            # Classify claim category (FACTUAL, OPINION, UNVERIFIABLE)
            category = classify_claim(claim.text)
            claim.type = category

            if category == "FACTUAL" and claim.verifiable:
                logger.info(f"Retrieving evidence for factual claim: '{claim.text[:40]}...'")
                evidence_items = self.retriever.retrieve(claim.text, top_k=3)

                # FIX 14: Evidence Quality Gate
                if not evidence_items:
                    logger.info(f"No evidence retrieved for claim '{claim.text[:40]}...'; marking INSUFFICIENT.")
                    claim.evidence = []
                    claim.verdict = VerificationVerdict.INSUFFICIENT
                else:
                    evidence_passages = [
                        item.get("evidence_text", "")
                        for item in evidence_items
                        if item.get("evidence_text")
                    ]
                    claim.evidence = evidence_passages
                    claim_evidence_items_map[claim.id] = evidence_items
            else:
                claim.evidence = []
                claim.verdict = VerificationVerdict.INSUFFICIENT

            processed_claims.append(claim)

        # Step 3b: Stance Verification (Phase 2)
        for claim in processed_claims:
            if claim.type == "FACTUAL" and claim.verifiable and claim.id in claim_evidence_items_map:
                evidence_items = claim_evidence_items_map[claim.id]
                logger.info(f"Verifying claim stance with model {self.verifier.model} for claim: '{claim.text[:40]}...'")
                verdict = self.verifier.verify_claim(claim, evidence_items)
                claim.verdict = verdict

        # Step 4: Trust Score & Hallucination Percentage Calculation
        trust_score = self.trust_calculator.calculate_score(processed_claims)
        hallucination_pct = self.trust_calculator.calculate_hallucination_percentage(processed_claims)

        logger.info(
            f"Verification pipeline completed successfully. Processed {len(processed_claims)} claims. "
            f"Trust Score: {trust_score:.1f}/100 | Hallucination Percentage: {hallucination_pct:.1f}%"
        )

        return VerificationReport(
            question=question,
            response=response_text,
            claims=processed_claims,
            trust_score=trust_score,
            hallucination_percentage=hallucination_pct,
            status="COMPLETED"
        )
