import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from backend.app.config import settings
    from backend.app.services.knowledge_base import KnowledgeBaseLoaderService
except ImportError:
    from app.config import settings
    from app.services.knowledge_base import KnowledgeBaseLoaderService

logger = logging.getLogger(__name__)


class VectorStoreInterface:
    """
    Lightweight In-Memory Vector Store & Document Chunk Repository.
    Loads legal corpus chunks from JSONL or directly via KnowledgeBaseLoaderService.
    Provides fast metadata lookup and retrieval access for the unified legal corpus.
    """

    def __init__(self, chunks_path: Optional[Path] = None, use_kb_service: bool = False):
        self.chunks_path = chunks_path or settings.KB_CHUNKS_PATH
        self.use_kb_service = use_kb_service
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_map: Dict[str, Dict[str, Any]] = {}

        self._load_chunks()

    def _load_chunks(self) -> None:
        """Load legal passage chunks from file or KnowledgeBaseLoaderService into memory."""
        if self.use_kb_service or not Path(self.chunks_path).exists():
            try:
                kb_loader = KnowledgeBaseLoaderService()
                legal_chunks = kb_loader.chunk_legal_corpus()
                self.chunks = [c.to_dict() for c in legal_chunks]
                self.chunk_map = {c["chunk_id"]: c for c in self.chunks}
                logger.info(f"Loaded {len(self.chunks)} unified legal chunks via KnowledgeBaseLoaderService.")
                return
            except Exception as e:
                logger.error(f"Error loading chunks via KnowledgeBaseLoaderService: {e}")
                if not Path(self.chunks_path).exists():
                    raise RuntimeError(f"Failed to load chunks via KnowledgeBaseLoaderService: {e}") from e

        try:
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        chunk = json.loads(line)
                        self.chunks.append(chunk)
                        chunk_id = chunk.get("chunk_id")
                        if chunk_id:
                            self.chunk_map[chunk_id] = chunk

            logger.info(f"Loaded {len(self.chunks)} legal passage chunks into VectorStore from file.")
        except Exception as e:
            logger.error(f"Error loading chunks from {self.chunks_path}: {e}")
            raise RuntimeError(f"Failed to load chunks dataset: {e}") from e

    def load_from_knowledge_base(self) -> None:
        """Explicitly reload vector store using KnowledgeBaseLoaderService."""
        kb_loader = KnowledgeBaseLoaderService()
        legal_chunks = kb_loader.chunk_legal_corpus()
        self.chunks = [c.to_dict() for c in legal_chunks]
        self.chunk_map = {c["chunk_id"]: c for c in self.chunks}
        logger.info(f"VectorStore reloaded with {len(self.chunks)} unified legal chunks.")

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chunk by its chunk_id."""
        return self.chunk_map.get(chunk_id)

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Return all loaded document chunks."""
        return self.chunks

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback simple keyword search over chunk text.
        """
        if not query or not query.strip():
            return []

        query_terms = set(query.lower().split())
        scored_chunks = []

        for chunk in self.chunks:
            text = chunk.get("text", "").lower()
            matches = sum(1 for term in query_terms if term in text)
            if matches > 0:
                scored_chunk = dict(chunk)
                scored_chunk["score"] = float(matches)
                scored_chunks.append(scored_chunk)

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
