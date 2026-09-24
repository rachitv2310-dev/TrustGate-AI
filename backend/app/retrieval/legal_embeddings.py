import logging
import math
from typing import List, Optional
import requests

try:
    from backend.app.config import settings
except ImportError:
    from app.config import settings

logger = logging.getLogger(__name__)


class LegalEmbeddingService:
    """
    Dense Legal Vector Embedding Service for Indian legal text queries and document chunks.
    Communicates with local Ollama instance via /api/embed using shb/legal-embed (768d).
    Uses 'search_query: ' for queries and 'search_document: ' for document passages.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        self.model_name = model_name or getattr(settings, "LEGAL_EMBEDDING_MODEL", "shb/legal-embed")
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.endpoint = f"{self.base_url}/api/embed"
        self.timeout = timeout
        self.expected_dim = 768

    def _call_ollama_embed(self, formatted_input: str) -> List[float]:
        """Send POST request to Ollama /api/embed endpoint and validate output."""
        if not formatted_input or not formatted_input.strip():
            return [0.0] * self.expected_dim

        payload = {
            "model": self.model_name,
            "input": formatted_input.strip(),
            "keep_alive": "5m"
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            embeddings = data.get("embeddings", [])
            if not embeddings or not isinstance(embeddings, list) or len(embeddings) == 0:
                raise ValueError(f"No embeddings returned from Ollama API for model {self.model_name}")

            vec = embeddings[0]
            if not isinstance(vec, list):
                raise ValueError("Returned embedding vector is not a list")

            if len(vec) != self.expected_dim:
                raise ValueError(
                    f"Dimension mismatch from model {self.model_name}: got {len(vec)}, expected {self.expected_dim}"
                )

            # Validate numeric values and check for NaN/Inf
            for val in vec:
                if not isinstance(val, (int, float)):
                    raise ValueError(f"Non-numeric value in embedding vector: {val}")
                if math.isnan(val) or math.isinf(val):
                    raise ValueError("Embedding vector contains NaN or Inf values")

            return vec

        except requests.RequestException as exc:
            logger.error(f"HTTP request error calling Ollama embed API ({self.model_name}): {exc}")
            raise RuntimeError(f"Failed to communicate with Ollama embed endpoint: {exc}") from exc
        except Exception as exc:
            logger.error(f"Error generating legal embedding: {exc}")
            raise

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate 768-dimensional vector embedding for a search query.
        Prefixes query with 'search_query: '.
        """
        if not query or not query.strip():
            return [0.0] * self.expected_dim

        formatted = f"search_query: {query.strip()}"
        return self._call_ollama_embed(formatted)

    def generate_document_embedding(self, text: str) -> List[float]:
        """
        Generate 768-dimensional vector embedding for a document chunk.
        Prefixes text with 'search_document: '.
        """
        if not text or not text.strip():
            return [0.0] * self.expected_dim

        formatted = f"search_document: {text.strip()}"
        return self._call_ollama_embed(formatted)

    def generate_document_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate 768-dimensional vector embeddings for a batch of document chunks efficiently.
        Prefixes each text with 'search_document: '.
        """
        if not texts:
            return []

        formatted_inputs = [
            f"search_document: {t.strip()}" if t and t.strip() else "search_document: empty"
            for t in texts
        ]

        payload = {
            "model": self.model_name,
            "input": formatted_inputs
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            embeddings = data.get("embeddings", [])
            if not embeddings or len(embeddings) != len(texts):
                raise ValueError(f"Batch embedding count mismatch: got {len(embeddings)}, expected {len(texts)}")

            validated_batch = []
            for vec in embeddings:
                if not isinstance(vec, list) or len(vec) != self.expected_dim:
                    raise ValueError(f"Vector dimension mismatch in batch: got {len(vec) if isinstance(vec, list) else 'invalid'}")
                for val in vec:
                    if math.isnan(val) or math.isinf(val):
                        raise ValueError("Batch vector contains NaN or Inf values")
                validated_batch.append(vec)

            return validated_batch

        except requests.RequestException as exc:
            logger.error(f"HTTP error calling Ollama batch embed API ({self.model_name}): {exc}")
            raise RuntimeError(f"Failed batch communicate with Ollama embed endpoint: {exc}") from exc

    def generate_embedding(self, text: str, is_query: bool = True) -> List[float]:
        """
        Generic embedding generation method.
        Defaults to search_query format if is_query=True, else search_document.
        """
        if is_query:
            return self.generate_query_embedding(text)
        return self.generate_document_embedding(text)
