import logging
from pathlib import Path
from typing import List, Optional
import joblib
import numpy as np
try:
    from backend.app.config import settings
except ImportError:
    from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Dense Vector Embedding Service for legal text queries.
    Uses pre-trained TF-IDF + TruncatedSVD (128d) model artifacts.
    Do NOT fit or retrain models at runtime.
    """

    def __init__(
        self,
        vectorizer_path: Optional[Path] = None,
        svd_path: Optional[Path] = None,
    ):
        self.vectorizer_path = vectorizer_path or settings.KB_VECTORIZER_PATH
        self.svd_path = svd_path or settings.KB_SVD_MODEL_PATH
        self._vectorizer = None
        self._svd_model = None

        self._load_models()

    def _load_models(self) -> None:
        """Load pre-trained vectorizer and SVD model artifacts."""
        if not Path(self.vectorizer_path).exists():
            raise FileNotFoundError(
                f"Vectorizer model artifact not found at: {self.vectorizer_path}"
            )
        if not Path(self.svd_path).exists():
            raise FileNotFoundError(
                f"SVD model artifact not found at: {self.svd_path}"
            )

        try:
            self._vectorizer = joblib.load(self.vectorizer_path)
            self._svd_model = joblib.load(self.svd_path)
            logger.info("Successfully loaded dense embedding vectorizer and SVD models.")
        except Exception as e:
            logger.error(f"Error loading embedding model artifacts: {e}")
            raise RuntimeError(f"Failed to load embedding models: {e}") from e

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate dense 128-dimensional L2-normalized vector embedding for text.
        """
        if not text or not text.strip():
            return [0.0] * 128

        tfidf_vec = self._vectorizer.transform([text.strip()])
        dense_vec = self._svd_model.transform(tfidf_vec)[0]

        # L2 Normalization
        norm = np.linalg.norm(dense_vec)
        if norm > 0:
            dense_vec = dense_vec / norm

        return dense_vec.astype(float).tolist()
