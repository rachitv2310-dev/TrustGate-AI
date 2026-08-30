import logging
from typing import Dict, Any, Optional

import requests

from backend.app.config import settings


logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service wrapper for interacting with local Ollama LLM instance.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:

        target_model = model or settings.CLAIM_EXTRACTION_MODEL

        url = f"{self.base_url}/api/generate"

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False
        }

        logger.info(
            "Sending request to Ollama using model: %s",
            target_model
        )

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

            return {
                "model": data.get("model", target_model),
                "response": data.get("response", "")
            }

        except requests.RequestException as exc:
            logger.error("Ollama request failed: %s", exc)
            raise RuntimeError(
                f"Failed to communicate with Ollama: {exc}"
            ) from exc