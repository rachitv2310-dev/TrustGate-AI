import logging
import re
from typing import List, Dict, Any, Optional

try:
    from backend.app.retrieval.lexical_retriever import LexicalRetriever
    from backend.app.retrieval.semantic_retriever import SemanticRetriever
    from backend.app.retrieval.legal_semantic_retriever import LegalSemanticRetriever
except ImportError:
    from app.retrieval.lexical_retriever import LexicalRetriever
    from app.retrieval.semantic_retriever import SemanticRetriever
    from app.retrieval.legal_semantic_retriever import LegalSemanticRetriever

logger = logging.getLogger(__name__)

LEGAL_STOPWORDS = {
    "what", "is", "the", "for", "a", "an", "of", "to", "in", "or", "and", "does",
    "deal", "with", "punishment", "punishments", "penalty", "under", "bharatiya",
    "nyaya", "sanhita", "act", "code", "section", "sec", "law", "prescribed",
    "prescribe", "bns", "ipc", "crpc", "tell", "me", "about", "which", "how", "much",
    "2023", "2024", "2025", "1860", "1973"
}


def extract_query_concepts(text: str) -> List[str]:
    """Extract non-stopword meaningful legal terms from query."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    words = [w.strip() for w in cleaned.split() if w.strip()]
    return [w for w in words if w not in LEGAL_STOPWORDS and not w.isdigit()]


class HybridRetriever:
    """
    Hybrid Search Retriever combining Lexical (BM25) and Dense Semantic retrieval.
    Applies Min-Max Score Normalization and weighted score fusion with deterministic
    legal section number matching and heading concept precision boost.
    Supports both TF-IDF/SVD ('tfidf') and shb/legal-embed ('legal_embed') dense semantic backends.
    """

    def __init__(
        self,
        lexical_retriever: Optional[LexicalRetriever] = None,
        semantic_retriever: Optional[Any] = None,
        alpha: float = 0.5,
        candidate_k: int = 50,
        semantic_backend: str = "tfidf",
    ):
        self.lexical = lexical_retriever or LexicalRetriever()
        self.alpha = alpha
        self.candidate_k = candidate_k
        self.semantic_backend = semantic_backend

        self._tfidf_semantic = None
        self._legal_semantic = None

        if semantic_retriever is not None:
            self.semantic = semantic_retriever
        else:
            if semantic_backend == "legal_embed":
                self._legal_semantic = LegalSemanticRetriever()
                self.semantic = self._legal_semantic
            else:
                self._tfidf_semantic = SemanticRetriever()
                self.semantic = self._tfidf_semantic

    def _get_semantic_retriever(self, backend: str) -> Any:
        if backend == "legal_embed":
            if self._legal_semantic is None:
                self._legal_semantic = LegalSemanticRetriever()
            return self._legal_semantic
        elif backend == "tfidf":
            if self._tfidf_semantic is None:
                self._tfidf_semantic = SemanticRetriever()
            return self._tfidf_semantic
        else:
            return self.semantic

    def search(
        self,
        query: str,
        alpha: Optional[float] = None,
        top_k: int = 5,
        semantic_backend: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval by combining lexical and semantic candidate pools.
        Returns top-k hybrid scored candidates.
        """
        if not query or not query.strip():
            return []

        fusion_alpha = alpha if alpha is not None else self.alpha
        active_backend = semantic_backend or self.semantic_backend
        semantic_retriever = self._get_semantic_retriever(active_backend) if semantic_backend else self.semantic

        bm25_res = self.lexical.search(query, top_k=self.candidate_k)
        dense_res = semantic_retriever.search(query, top_k=self.candidate_k)

        # Union of candidate pools
        candidates_dict: Dict[str, Dict[str, Any]] = {}

        for item in bm25_res:
            cid = item["chunk_id"]
            candidates_dict[cid] = {
                "item": item,
                "bm25_raw": item.get("score", 0.0),
                "dense_raw": 0.0,
            }

        for item in dense_res:
            cid = item["chunk_id"]
            if cid in candidates_dict:
                candidates_dict[cid]["dense_raw"] = item.get("score", 0.0)
            else:
                candidates_dict[cid] = {
                    "item": item,
                    "bm25_raw": 0.0,
                    "dense_raw": item.get("score", 0.0),
                }

        c_list = list(candidates_dict.values())
        if not c_list:
            return []

        # Min-Max Normalization over candidate set (FIX 5: safe zero handling)
        bm25_scores = [c["bm25_raw"] for c in c_list]
        dense_scores = [c["dense_raw"] for c in c_list]

        min_b, max_b = min(bm25_scores), max(bm25_scores)
        min_d, max_d = min(dense_scores), max(dense_scores)

        # Explicit section reference detection (e.g. "Section 303" -> "303")
        explicit_sec = None
        sec_match_regex = re.search(r"\b(?:section|sec)\s*(\d+)\b", query.lower())
        if sec_match_regex:
            explicit_sec = sec_match_regex.group(1)

        q_concepts = extract_query_concepts(query)

        for c in c_list:
            if max_b > min_b:
                c["bm25_norm"] = (c["bm25_raw"] - min_b) / (max_b - min_b)
            else:
                c["bm25_norm"] = 1.0 if c["bm25_raw"] > 0 else 0.0

            if max_d > min_d:
                c["dense_norm"] = (c["dense_raw"] - min_d) / (max_d - min_d)
            else:
                c["dense_norm"] = 1.0 if c["dense_raw"] > 0 else 0.0

            # Heading concept precision calculation
            c_heading_raw = c["item"].get("section_heading", "").strip().lower()
            c_heading_raw = re.sub(r"\s+", " ", c_heading_raw)
            c_heading_words = extract_query_concepts(c_heading_raw)

            f_heading = 0.0
            if q_concepts and c_heading_words:
                matched_h = [t for t in set(q_concepts) if t in c_heading_words]
                if set(q_concepts).issubset(set(c_heading_words)):
                    precision = len(set(q_concepts)) / len(c_heading_words)
                    f_heading = 0.5 + 0.5 * precision
                elif matched_h:
                    f_heading = (len(matched_h) / len(set(q_concepts))) * 0.5

            # Explicit section match boost
            f_section = 0.0
            if explicit_sec and str(c["item"].get("section_number")) == str(explicit_sec):
                f_section = 1.0

            base_hybrid = fusion_alpha * c["bm25_norm"] + (1.0 - fusion_alpha) * c["dense_norm"]
            if explicit_sec:
                hybrid_score = 0.50 * base_hybrid + 0.40 * f_section + 0.10 * f_heading
            else:
                hybrid_score = 0.70 * base_hybrid + 0.30 * f_heading

            c["hybrid_score"] = float(round(hybrid_score, 4))

        # Deterministic sorting: hybrid_score descending, chunk_id ascending
        c_list.sort(key=lambda x: (x["hybrid_score"], x["item"]["chunk_id"]), reverse=True)

        results = []
        for rank, c in enumerate(c_list[:top_k], 1):
            it = c["item"]
            results.append({
                "rank": rank,
                "chunk_id": it["chunk_id"],
                "score": c["hybrid_score"],
                "hybrid_score": c["hybrid_score"],
                "bm25_raw_score": float(round(c["bm25_raw"], 4)),
                "bm25_normalized_score": float(round(c["bm25_norm"], 4)),
                "dense_raw_score": float(round(c["dense_raw"], 4)),
                "dense_normalized_score": float(round(c["dense_norm"], 4)),
                "document_id": it.get("document_id", "BNS_2023"),
                "document_type": it.get("document_type", "STATUTE"),
                "chapter_number": it.get("chapter_number", ""),
                "section_number": it.get("section_number", ""),
                "section_heading": it.get("section_heading", ""),
                "source_authority": it.get("source_authority", "India Code"),
                "source_url": it.get("source_url", ""),
                "verification_status": it.get("verification_status", "UNVERIFIED"),
                "page_start": it.get("page_start", 0),
                "page_end": it.get("page_end", 0),
                "text": it.get("text", ""),
            })

        return results