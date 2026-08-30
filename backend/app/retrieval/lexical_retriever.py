import json
import logging
import math
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional
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
        """Deterministic legal tokenization."""
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

            # Rebuild doc_freqs from chunks for BM25 term matching
            self.doc_freqs = []
            for c in self.chunks:
                text_to_index = f"Section {c['section_number']} {c['section_heading']} {c['chapter_title']} {c['text']}"
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

        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for idx, df_dict in enumerate(self.doc_freqs):
                tf = df_dict.get(token, 0)
                if tf > 0:
                    num = tf * (self.k1 + 1.0)
                    den = tf + self.k1 * (1.0 - self.b + self.b * (self.doc_len[idx] / self.avgdl))
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
                "chapter_number": chunk.get("chapter_number", ""),
                "section_number": chunk.get("section_number", ""),
                "section_heading": chunk.get("section_heading", ""),
                "page_start": chunk.get("page_start", 0),
                "page_end": chunk.get("page_end", 0),
                "text": chunk.get("text", ""),
            })

        return results
