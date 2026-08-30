import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

STOPWORDS = {"what", "is", "the", "for", "a", "an", "of", "to", "in", "or", "and", "does", "deal", "with", "punishment"}


def clean_words(text: str) -> List[str]:
    """Extract non-stopword content words from text."""
    return [
        w.strip()
        for w in re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower()).split()
        if w.strip() and w.strip() not in STOPWORDS
    ]


class EvidenceReranker:
    """
    Multi-Feature Cross-Feature Evidence Reranker for retrieved legal passages.
    Weights:
    - Hybrid score (0.25)
    - Normalized BM25 (0.15)
    - Normalized Dense (0.15)
    - Query term coverage (0.10)
    - Exact term overlap (0.10)
    - Phrase match (0.05)
    - Section reference match (0.05)
    - Heading match (0.15)
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "hybrid_score": 0.25,
            "normalized_bm25": 0.15,
            "normalized_dense": 0.15,
            "query_term_coverage": 0.10,
            "exact_term_overlap": 0.10,
            "phrase_match": 0.05,
            "section_match": 0.05,
            "heading_match": 0.15,
        }

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Deterministic legal tokenization."""
        cleaned = re.sub(r"[^a-zA-Z0-9\s\-]", " ", text.lower())
        tokens = [t.strip("-") for t in cleaned.split() if len(t.strip("-")) > 0]
        return tokens

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidate evidence snippets based on multi-feature legal relevance.
        Returns top-k reranked evidence dictionaries.
        """
        if not candidates:
            return []

        if not query or not query.strip():
            return candidates[:top_k]

        q_tokens = self.tokenize(query)
        q_concepts = clean_words(query)
        q_phrase = " ".join(q_tokens)

        # Check explicit section reference (e.g. "Section 103" or "Section 318")
        sec_ref = None
        sec_match_regex = re.search(r"\b(?:section|sec)\s*(\d+)\b", query.lower())
        if sec_match_regex:
            sec_ref = sec_match_regex.group(1)

        features_list = []
        for c in candidates:
            chunk_text = c.get("text", "")
            c_tokens = set(self.tokenize(chunk_text))
            c_heading_raw = c.get("section_heading", "").strip().lower()
            c_heading_words = set(clean_words(c_heading_raw))

            f_hybrid = c.get("hybrid_score", c.get("score", 0.0))
            f_bm25 = c.get("bm25_normalized_score", c.get("bm25_score", 0.0))
            f_dense = c.get("dense_normalized_score", c.get("dense_score", 0.0))

            # Query Term Coverage
            if q_tokens:
                matched_terms = [t for t in set(q_tokens) if t in c_tokens]
                f_coverage = len(matched_terms) / len(set(q_tokens))
            else:
                f_coverage = 0.0

            # Exact Term Overlap
            f_overlap = f_coverage

            # Phrase Match
            f_phrase = 0.0
            if q_phrase and len(q_tokens) > 1:
                clean_chunk = " ".join(self.tokenize(chunk_text))
                if q_phrase in clean_chunk:
                    f_phrase = 1.0

            # Section Reference Match
            f_section = 0.0
            if sec_ref and str(c.get("section_number")) == str(sec_ref):
                f_section = 1.0

            # Heading Match: Precision and primary section concept matching
            f_heading = 0.0
            if q_tokens and c_heading_words:
                matched_h = [t for t in set(q_tokens) if t in c_heading_words]
                if matched_h:
                    if any(concept in c_heading_words for concept in q_concepts) and len(c_heading_words) <= 2:
                        f_heading = 1.0
                    else:
                        f_heading = len(matched_h) / len(set(q_tokens))

            # Weighted Rerank Score
            rerank_score = (
                self.weights["hybrid_score"] * f_hybrid
                + self.weights["normalized_bm25"] * f_bm25
                + self.weights["normalized_dense"] * f_dense
                + self.weights["query_term_coverage"] * f_coverage
                + self.weights["exact_term_overlap"] * f_overlap
                + self.weights["phrase_match"] * f_phrase
                + self.weights["section_match"] * f_section
                + self.weights["heading_match"] * f_heading
            )

            features_list.append({
                "candidate": c,
                "rerank_score": float(round(rerank_score, 4)),
                "features": {
                    "hybrid_score": float(round(f_hybrid, 4)),
                    "normalized_bm25": float(round(f_bm25, 4)),
                    "normalized_dense": float(round(f_dense, 4)),
                    "query_term_coverage": float(round(f_coverage, 4)),
                    "exact_term_overlap": float(round(f_overlap, 4)),
                    "phrase_match": float(round(f_phrase, 4)),
                    "section_match": float(round(f_section, 4)),
                    "heading_match": float(round(f_heading, 4)),
                },
            })

        # Deterministic Tie Breaking
        def tie_break_key(x):
            c = x["candidate"]
            sec_num_int = int(c["section_number"]) if str(c.get("section_number", "")).isdigit() else 9999
            return (
                x["rerank_score"],
                c.get("hybrid_score", 0.0),
                c.get("dense_raw_score", c.get("dense_score", 0.0)),
                c.get("bm25_raw_score", c.get("bm25_score", 0.0)),
                -sec_num_int,
                x["candidate"].get("chunk_id", ""),
            )

        features_list.sort(key=tie_break_key, reverse=True)

        results = []
        for rank, f_obj in enumerate(features_list[:top_k], 1):
            c = f_obj["candidate"]
            item = dict(c)
            item["rank"] = rank
            item["score"] = f_obj["rerank_score"]
            item["rerank_score"] = f_obj["rerank_score"]
            item["features"] = f_obj["features"]
            results.append(item)

        return results
