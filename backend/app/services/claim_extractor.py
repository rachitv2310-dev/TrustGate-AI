from typing import List

from backend.app.schemas.claim import Claim
from backend.app.config import settings
from backend.app.services.llm_service import OllamaService


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

        prompt = f"""
You are a legal claim extraction system.

Extract the atomic, factual claims from the following AI-generated response.

Rules:
1. Extract only factual or legally verifiable claims.
2. Split compound statements into separate atomic claims.
3. Do not add information that is not present in the response.
4. Return one claim per line.
5. Return ONLY the claims, without numbering, explanations, or extra text.

AI-generated response:
{text}
"""

        result = self.llm.generate(
            prompt=prompt,
            model=self.model
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

        for index, line in enumerate(lines, start=1):
            # Remove common numbering formats such as:
            # 1. Claim
            # 2) Claim
            # - Claim
            cleaned = line.lstrip("-• ").strip()

            if ". " in cleaned and cleaned.split(". ", 1)[0].isdigit():
                cleaned = cleaned.split(". ", 1)[1].strip()

            if ") " in cleaned and cleaned.split(") ", 1)[0].isdigit():
                cleaned = cleaned.split(") ", 1)[1].strip()

            if cleaned:
                claims.append(
                    Claim(
                        id=f"claim-{index}",
                        text=cleaned,
                        type="FACTUAL"
                    )
                )

        return claims