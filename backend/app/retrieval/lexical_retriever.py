import json
import logging
import math
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional

try:
    from backend.app.config import settings
except ImportError:
    from app.config import settings

logger = logging.getLogger(__name__)


class LexicalRetriever:
    """
    Lexical Search Retriever using pre-indexed Okapi BM25 index over legal corpus.
    Loads bm25_index.json and BNS_2023_chunks.jsonl without rebuilding index at runtime.
    """

    def __init__(
        self,
        index_path: Optional[Path] = None,
        chunks_path: Optional[Path] = None,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.index_path = index_path or settings.KB_BM25_INDEX_PATH
        self.chunks_path = chunks_path or settings.KB_CHUNKS_PATH
        self.k1 = k1
        self.b = b

        self.chunks: List[Dict[str, Any]] = []
        self.corpus_size: int = 0
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self.doc_freqs: List[Counter] = []
        self.idf: Dict[str, float] = {}

        self._load_index()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Deterministic legal tokenization with normalized whitespace."""
        cleaned = re.sub(r"[^a-zA-Z0-9\s\-]", " ", text.lower())
        tokens = [t.strip("-") for t in cleaned.split() if len(t.strip("-")) > 0]
        return tokens

    def _load_index(self) -> None:
        """Load pre-built BM25 index and chunk corpus into memory."""
        if not Path(self.index_path).exists():
            raise FileNotFoundError(f"BM25 index file not found at: {self.index_path}")
        if not Path(self.chunks_path).exists():
            raise FileNotFoundError(f"Chunks dataset file not found at: {self.chunks_path}")

        try:
            # Load chunks
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                self.chunks = [json.loads(line) for line in f if line.strip()]

            # Load index metadata
            with open(self.index_path, "r", encoding="utf-8") as f:
                idx_data = json.load(f)

            self.k1 = idx_data.get("k1", self.k1)
            self.b = idx_data.get("b", self.b)
            self.corpus_size = idx_data.get("corpus_size", len(self.chunks))
            self.avgdl = idx_data.get("avgdl", 0.0)
            self.idf = idx_data.get("idf", {})
            self.doc_len = idx_data.get("doc_len", [])

            # Validation checks (FIX 3)
            if len(self.chunks) != self.corpus_size:
                raise ValueError(
                    f"Corpus chunk count ({len(self.chunks)}) does not match BM25 index corpus_size ({self.corpus_size})."
                )

            if self.doc_len and len(self.chunks) != len(self.doc_len):
                raise ValueError(
                    f"Corpus chunk count ({len(self.chunks)}) does not match BM25 index doc_len count ({len(self.doc_len)})."
                )

            index_chunk_ids = idx_data.get("chunk_ids")
            if index_chunk_ids:
                actual_chunk_ids = [c["chunk_id"] for c in self.chunks]
                if actual_chunk_ids != index_chunk_ids:
                    raise ValueError("BM25 index chunk_ids do not match corpus chunk IDs in exact order.")

            # Rebuild doc_freqs from chunks using canonical indexing format (FIX 1)
            self.doc_freqs = []
            for c in self.chunks:
                sec_num = c.get("section_number", "")
                sec_head = c.get("section_heading", "")
                chap_title = c.get("chapter_title", "")
                text_content = c.get("text", "")
                text_to_index = f"Section {sec_num} {sec_head} {chap_title} {text_content}"
                self.doc_freqs.append(Counter(self.tokenize(text_to_index)))

            logger.info(
                f"Successfully loaded LexicalRetriever BM25 index ({self.corpus_size} chunks, {len(self.idf)} terms)."
            )
        except Exception as e:
            logger.error(f"Error loading LexicalRetriever BM25 index: {e}")
            raise RuntimeError(f"Failed to load BM25 index: {e}") from e

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform BM25 keyword search against loaded legal corpus.
        Returns top-k candidate dictionaries.
        """
        if not query or not query.strip():
            return []

        query_tokens = self.tokenize(query)
        scores = [0.0] * self.corpus_size
        avgdl_safe = self.avgdl if self.avgdl > 0 else 1.0

        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for idx, df_dict in enumerate(self.doc_freqs):
                tf = df_dict.get(token, 0)
                if tf > 0:
                    d_len = self.doc_len[idx] if idx < len(self.doc_len) else avgdl_safe
                    num = tf * (self.k1 + 1.0)
                    den = tf + self.k1 * (1.0 - self.b + self.b * (d_len / avgdl_safe))
                    scores[idx] += idf_val * (num / den)

        # Sort score descending, tie-break by chunk_id ascending
        indexed_results = list(enumerate(scores))
        indexed_results.sort(key=lambda x: (x[1], -x[0]), reverse=True)

        results = []
        for rank, (doc_idx, score) in enumerate(indexed_results[:top_k], 1):
            if score <= 0.0 and len(results) > 0:
                break
            chunk = self.chunks[doc_idx]
            results.append({
                "rank": rank,
                "chunk_id": chunk["chunk_id"],
                "score": float(round(score, 4)),
                "bm25_score": float(round(score, 4)),
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
