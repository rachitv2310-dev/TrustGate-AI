import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np

try:
    from backend.app.config import settings
    from backend.app.retrieval.embeddings import EmbeddingService
except ImportError:
    from app.config import settings
    from app.retrieval.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class SemanticRetriever:
    """
    Dense Vector / Semantic Search Retriever.
    Uses pre-built LSA/SVD dense vector matrix (dense_embeddings.npy) and 
    EmbeddingService for query vector generation.
    Computes cosine similarity over loaded legal passage vectors.
    """

    def __init__(
        self,
        embeddings_path: Optional[Path] = None,
        chunks_path: Optional[Path] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.embeddings_path = embeddings_path or settings.KB_DENSE_EMBEDDINGS_PATH
        self.chunks_path = chunks_path or settings.KB_CHUNKS_PATH
        self.embedding_service = embedding_service or EmbeddingService()

        self.embeddings: Optional[np.ndarray] = None
        self.chunks: List[Dict[str, Any]] = []

        self._load_dense_index()

    def _load_dense_index(self) -> None:
        """Load dense embeddings numpy matrix and chunk corpus metadata with strict validation."""
        if not Path(self.embeddings_path).exists():
            raise FileNotFoundError(f"Dense embeddings file not found at: {self.embeddings_path}")
        if not Path(self.chunks_path).exists():
            raise FileNotFoundError(f"Chunks dataset file not found at: {self.chunks_path}")

        try:
            self.embeddings = np.load(self.embeddings_path)
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                self.chunks = [json.loads(line) for line in f if line.strip()]

            # FIX 4: Strict validation checks
            if self.embeddings is None or self.embeddings.ndim != 2:
                raise ValueError(f"Invalid dense embeddings matrix shape: {getattr(self.embeddings, 'shape', None)}")

            if len(self.chunks) != self.embeddings.shape[0]:
                raise ValueError(
                    f"Dense embeddings row count ({self.embeddings.shape[0]}) does not match corpus chunk count ({len(self.chunks)})."
                )

            if np.isnan(self.embeddings).any() or np.isinf(self.embeddings).any():
                raise ValueError("Dense embeddings matrix contains invalid NaN or Inf values.")

            logger.info(
                f"Successfully loaded SemanticRetriever dense index (shape: {self.embeddings.shape})."
            )
        except Exception as e:
            logger.error(f"Error loading SemanticRetriever dense index: {e}")
            raise RuntimeError(f"Failed to load dense index: {e}") from e

    def search_by_vector(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform cosine similarity search given an already generated query vector."""
        if not query_vector or self.embeddings is None:
            return []

        q_vec = np.array(query_vector, dtype=float)
        if len(q_vec) != self.embeddings.shape[1]:
            logger.error(
                f"Query vector dimension mismatch: got {len(q_vec)}, expected {self.embeddings.shape[1]}"
            )
            return []

        # FIX 5: Zero-vector or NaN query handling
        if np.isnan(q_vec).any() or np.isinf(q_vec).any():
            logger.warning("Query vector contains NaN or Inf values; returning empty semantic results.")
            return []

        norm = np.linalg.norm(q_vec)
        if norm == 0 or np.isnan(norm):
            logger.warning("Query vector is a zero vector; returning empty semantic results.")
            return []

        q_vec = q_vec / norm

        # Cosine similarity matrix multiplication against L2-normalized embeddings
        scores = np.dot(self.embeddings, q_vec)

        # Sort score descending
        indexed_results = list(enumerate(scores))
        indexed_results.sort(key=lambda x: (x[1], -x[0]), reverse=True)

        results = []
        for rank, (doc_idx, score) in enumerate(indexed_results[:top_k], 1):
            if doc_idx >= len(self.chunks):
                continue
            chunk = self.chunks[doc_idx]
            results.append({
                "rank": rank,
                "chunk_id": chunk["chunk_id"],
                "score": float(round(score, 4)),
                "dense_score": float(round(score, 4)),
                "document_id": chunk.get("document_id", "BNS_2023"),
                "document_type": chunk.get("document_type", "STATUTE"),
                "chapter_number": chunk.get("chapter_number", ""),
                "section_number": chunk.get("section_number", ""),
                "section_heading": chunk.get("section_heading", chunk.get("case_name", "")),
                "source_authority": chunk.get("source_authority", "India Code"),
                "source_url": chunk.get("source_url", ""),
                "verification_status": chunk.get("verification_status", "UNVERIFIED"),
                "page_start": chunk.get("page_start", 0),
                "page_end": chunk.get("page_end", 0),
                "text": chunk.get("text", ""),
            })

        return results

    def search(
        self,
        query_or_vector: Union[str, List[float]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform dense semantic vector search for a text query or query vector.
        """
        if isinstance(query_or_vector, list):
            return self.search_by_vector(query_or_vector, top_k=top_k)

        query_text = str(query_or_vector)
        if not query_text or not query_text.strip():
            return []

        # Generate query vector using EmbeddingService
        query_vec = self.embedding_service.generate_embedding(query_text)
        return self.search_by_vector(query_vec, top_k=top_k)
