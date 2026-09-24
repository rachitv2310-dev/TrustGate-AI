import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

STOPWORDS = {
    "what", "is", "the", "for", "a", "an", "of", "to", "in", "or", "and", "does",
    "deal", "with", "punishment", "punishments", "penalty", "under", "bharatiya",
    "nyaya", "sanhita", "act", "code", "section", "sec", "law", "prescribed",
    "prescribe", "bns", "ipc", "crpc", "tell", "me", "about", "which", "how", "much"
}


def clean_words(text: str) -> List[str]:
    """Extract non-stopword meaningful legal terms from text."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    words = [w.strip() for w in cleaned.split() if w.strip()]
    return [w for w in words if w not in STOPWORDS]


class EvidenceReranker:
    """
    Multi-Feature Evidence Reranker for retrieved legal passages.
    Prioritizes explicit section number matching and exact heading legal concept precision
    over generic semantic similarity.
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

        q_tokens = set(self.tokenize(query))
        q_concepts = clean_words(query)

        # Detect explicit section reference (e.g. "Section 103", "sec 318", "303")
        sec_ref = None
        sec_match_regex = re.search(r"\b(?:section|sec)\s*(\d+)\b", query.lower())
        if sec_match_regex:
            sec_ref = sec_match_regex.group(1)

        features_list = []
        for c in candidates:
            chunk_text = c.get("text", "")
            c_tokens = set(self.tokenize(chunk_text))

            c_heading_raw = c.get("section_heading", "").strip().lower()
            c_heading_raw = re.sub(r"\s+", " ", c_heading_raw)
            c_heading_words = set(clean_words(c_heading_raw))
            c_heading_all_tokens = set(self.tokenize(c_heading_raw))

            f_hybrid = c.get("hybrid_score", c.get("score", 0.0))
            f_bm25 = c.get("bm25_normalized_score", c.get("bm25_score", 0.0))
            f_dense = c.get("dense_normalized_score", c.get("dense_score", 0.0))

            # 1. Query Term Coverage: Fraction of meaningful query concepts in candidate text body
            if q_concepts:
                matched_concepts = [t for t in q_concepts if t in c_tokens]
                f_coverage = len(matched_concepts) / len(q_concepts)
            else:
                f_coverage = 0.0

            # 2. Exact Term Overlap: Fraction of meaningful query concepts matching section heading
            if q_concepts and c_heading_words:
                matched_heading_concepts = [t for t in q_concepts if t in c_heading_words]
                f_overlap = len(matched_heading_concepts) / len(q_concepts)
            else:
                f_overlap = 0.0

            # 3. Phrase Match: Check if combined legal concepts appear contiguously in heading or body text
            f_phrase = 0.0
            if len(q_concepts) >= 2:
                concept_phrase = " ".join(q_concepts)
                clean_chunk_str = " ".join(self.tokenize(chunk_text))
                if concept_phrase in c_heading_raw:
                    f_phrase = 1.0
                elif concept_phrase in clean_chunk_str:
                    f_phrase = 0.75
                else:
                    # Check partial 2-gram overlap
                    for i in range(len(q_concepts) - 1):
                        pair = f"{q_concepts[i]} {q_concepts[i+1]}"
                        if pair in c_heading_raw or pair in clean_chunk_str:
                            f_phrase = max(f_phrase, 0.5)

            # 4. Section Reference Match
            f_section = 0.0
            if sec_ref and str(c.get("section_number")) == str(sec_ref):
                f_section = 1.0

            # 5. Heading Match: Precision ratio of matched concepts vs total heading words
            f_heading = 0.0
            if q_concepts and c_heading_words:
                matched_h = [t for t in set(q_concepts) if t in c_heading_words]
                if set(q_concepts).issubset(c_heading_words):
                    precision = len(set(q_concepts)) / len(c_heading_words)
                    f_heading = 0.5 + 0.5 * precision
                elif matched_h:
                    f_heading = (len(matched_h) / len(set(q_concepts))) * 0.5

            # Weighted Rerank Score Calculation
            if sec_ref:
                w = {
                    "hybrid_score": 0.15,
                    "normalized_bm25": 0.05,
                    "normalized_dense": 0.05,
                    "query_term_coverage": 0.10,
                    "exact_term_overlap": 0.15,
                    "phrase_match": 0.05,
                    "section_match": 0.35,
                    "heading_match": 0.10,
                }
            else:
                w = self.weights

            rerank_score = (
                w["hybrid_score"] * f_hybrid
                + w["normalized_bm25"] * f_bm25
                + w["normalized_dense"] * f_dense
                + w["query_term_coverage"] * f_coverage
                + w["exact_term_overlap"] * f_overlap
                + w["phrase_match"] * f_phrase
                + w["section_match"] * f_section
                + w["heading_match"] * f_heading
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
            cand = x["candidate"]
            sec_num_str = str(cand.get("section_number", ""))
            sec_num_int = int(sec_num_str) if sec_num_str.isdigit() else 9999
            return (
                x["rerank_score"],
                cand.get("hybrid_score", 0.0),
                cand.get("dense_raw_score", cand.get("dense_score", 0.0)),
                cand.get("bm25_raw_score", cand.get("bm25_score", 0.0)),
                -sec_num_int,
                cand.get("chunk_id", ""),
            )

        features_list.sort(key=tie_break_key, reverse=True)

        results = []
        for rank, f_obj in enumerate(features_list[:top_k], 1):
            cand = f_obj["candidate"]
            item = dict(cand)
            item["rank"] = rank
            item["score"] = f_obj["rerank_score"]
            item["rerank_score"] = f_obj["rerank_score"]
            item["features"] = f_obj["features"]
            results.append(item)

        return results
