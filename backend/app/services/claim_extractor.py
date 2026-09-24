import re
import logging
from typing import List

try:
    from backend.app.schemas.claim import Claim
    from backend.app.config import settings
    from backend.app.services.llm_service import OllamaService
except ImportError:
    from app.schemas.claim import Claim
    from app.config import settings
    from app.services.llm_service import OllamaService

logger = logging.getLogger(__name__)


class ClaimExtractorService:
    """
    Service responsible for parsing AI responses into atomic,
    testable claims using the configured Ollama LLM.
    """

    def __init__(self):
        self.model = settings.CLAIM_EXTRACTION_MODEL
        self.llm = OllamaService()

    def extract_claims(self, text: str) -> List[Claim]:
        """
        Extract atomic factual claims from an AI-generated response.
        """
        if not text or not text.strip():
            return []

        prompt = f"""You are a legal claim extraction parser.

Extract all atomic, standalone factual statements from the following AI response text.

Rules:
1. Split compound sentences into single atomic factual statements.
2. Preserve all legal reference information exactly as written in the text, including Section numbers, Act names (e.g., BNS, BNSS, BSA, IPC), and legal citations (e.g., "[Source: Section 304, BNSS 2023]"). Keep source and reference information attached to the corresponding claim.
3. Do NOT correct, rewrite, reinterpret, omit, or remove any legal references or section numbers.
4. Output one atomic claim per line.
5. Do NOT include introductory text, meta-comments, headings, numbering, or explanations.
6. Output ONLY the extracted claim lines.

AI Response Text:
{text}
"""

        result = self.llm.generate(
            prompt=prompt,
            model=self.model,
            options={"temperature": 0.0, "num_predict": 256},
            keep_alive="5m",
            timeout=180
        )

        raw_response = result.get("response", "").strip()

        if not raw_response:
            return []

        lines = [
            line.strip()
            for line in raw_response.splitlines()
            if line.strip()
        ]

        claims = []
        seen_normalized = set()  # FIX 12: Deduplication tracking

        for line in lines:
            # FIX 11: Parser hardening - strip meta-text, headers, and bullet markers
            cleaned = line.lstrip("-•*# ").strip()

            # Remove prefix numbering like 1. Claim, 2) Claim
            if ". " in cleaned and cleaned.split(". ", 1)[0].isdigit():
                cleaned = cleaned.split(". ", 1)[1].strip()
            elif ") " in cleaned and cleaned.split(") ", 1)[0].isdigit():
                cleaned = cleaned.split(") ", 1)[1].strip()

            # Ignore lines ending with ':' (headings/meta-text) or intro phrases
            cleaned_lower = cleaned.lower()
            if cleaned.endswith(":") or cleaned_lower.startswith(("here are", "the following", "extracted claim", "claims:", "note:")):
                continue

            # Ignore short noise (< 10 chars or < 2 words)
            if len(cleaned) < 10 or len(cleaned.split()) < 2:
                continue

            # Deduplication check (FIX 12)
            norm_key = re.sub(r"\s+", " ", cleaned_lower.rstrip("."))
            if norm_key in seen_normalized:
                continue

            seen_normalized.add(norm_key)
            claims.append(
                Claim(
                    id=f"claim-{len(claims) + 1}",
                    text=cleaned,
                    type="FACTUAL"
                )
            )

        return claims