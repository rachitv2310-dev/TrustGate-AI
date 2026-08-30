import logging
import re
from typing import List, Dict, Any, Optional
from app.retrieval.lexical_retriever import LexicalRetriever
from app.retrieval.semantic_retriever import SemanticRetriever

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid Search Retriever combining Lexical (BM25) and Dense Semantic retrieval.
    Applies Min-Max Score Normalization and weighted score fusion (default alpha = 0.50, candidate_k = 50).
    """

    def __init__(
        self,
        lexical_retriever: Optional[LexicalRetriever] = None,
        semantic_retriever: Optional[SemanticRetriever] = None,
        alpha: float = 0.5,
        candidate_k: int = 50,
    ):
        self.lexical = lexical_retriever or LexicalRetriever()
        self.semantic = semantic_retriever or SemanticRetriever()
        self.alpha = alpha
        self.candidate_k = candidate_k

    def search(
        self,
        query: str,
        alpha: Optional[float] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval by combining lexical and semantic candidate pools.
        Returns top-k hybrid scored candidates.
        """
        if not query or not query.strip():
            return []

        fusion_alpha = alpha if alpha is not None else self.alpha

        bm25_res = self.lexical.search(query, top_k=self.candidate_k)
        dense_res = self.semantic.search(query, top_k=self.candidate_k)

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

        # Min-Max Normalization over candidate set
        bm25_scores = [c["bm25_raw"] for c in c_list]
        dense_scores = [c["dense_raw"] for c in c_list]

        min_b, max_b = min(bm25_scores), max(bm25_scores)
        min_d, max_d = min(dense_scores), max(dense_scores)

        # Extract primary query concepts for heading precision matching
        stopwords = {"what", "is", "the", "for", "a", "an", "of", "to", "in", "or", "and", "does", "deal", "with", "punishment"}
        q_concepts = [
            w.strip()
            for w in re.sub(r"[^a-zA-Z0-9\s]", " ", query.lower()).split()
            if w.strip() and w.strip() not in stopwords
        ]

        for c in c_list:
            if max_b > min_b:
                c["bm25_norm"] = (c["bm25_raw"] - min_b) / (max_b - min_b)
            else:
                c["bm25_norm"] = 1.0 if c["bm25_raw"] > 0 else 0.0

            if max_d > min_d:
                c["dense_norm"] = (c["dense_raw"] - min_d) / (max_d - min_d)
            else:
                c["dense_norm"] = 1.0 if c["dense_raw"] > 0 else 0.0

            # Heading Match: Precision and primary section concept matching
            c_heading_raw = c["item"].get("section_heading", "").strip().lower()
            c_heading_words = set([
                w.strip()
                for w in re.sub(r"[^a-zA-Z0-9\s]", " ", c_heading_raw).split()
                if w.strip() and w.strip() not in stopwords
            ])
            f_heading = 0.0
            if q_concepts and c_heading_words:
                matched_h = [t for t in set(q_concepts) if t in c_heading_words]
                if matched_h:
                    if any(concept in c_heading_words for concept in q_concepts) and len(c_heading_words) <= 2:
                        f_heading = 1.0
                    else:
                        f_heading = len(matched_h) / len(c_heading_words)

            base_hybrid = fusion_alpha * c["bm25_norm"] + (1.0 - fusion_alpha) * c["dense_norm"]
            hybrid_score = 0.80 * base_hybrid + 0.20 * f_heading
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
                "chapter_number": it.get("chapter_number", ""),
                "section_number": it.get("section_number", ""),
                "section_heading": it.get("section_heading", ""),
                "page_start": it.get("page_start", 0),
                "page_end": it.get("page_end", 0),
                "text": it.get("text", ""),
            })

        return results
