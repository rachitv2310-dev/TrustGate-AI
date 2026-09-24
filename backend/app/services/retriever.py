import logging
from typing import List, Dict, Any, Union, Optional

try:
    from backend.app.schemas.claim import Claim
    from backend.app.retrieval.hybrid_retriever import HybridRetriever
    from backend.app.retrieval.reranker import EvidenceReranker
except ImportError:
    from app.schemas.claim import Claim
    from app.retrieval.hybrid_retriever import HybridRetriever
    from app.retrieval.reranker import EvidenceReranker

logger = logging.getLogger(__name__)


class EvidenceRetrieverService:
    """
    Stage 7 Retrieval Service orchestrating BM25 + Dense Hybrid Search and Multi-Feature Reranking.
    Searches the unified legal corpus (Stage 1 BNS sections + Stage 2 Supreme Court judgments)
    and returns top-K reranked legal evidence with complete provenance.
    """

    def __init__(
        self,
        hybrid_retriever: Optional[HybridRetriever] = None,
        reranker: Optional[EvidenceReranker] = None,
    ):
        self.hybrid_retriever = hybrid_retriever or HybridRetriever()
        self.reranker = reranker or EvidenceReranker()

    def retrieve(
        self,
        query: Union[str, Claim],
        top_k: int = 3,
        candidate_k: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Execute full retrieval pipeline: Claim -> Hybrid Search (BM25 + Dense) -> Candidate Reranker -> Top-K Evidence.
        Returns detailed evidence objects preserving full legal provenance.
        """
        if isinstance(query, Claim):
            query_text = getattr(query, "text", None) or getattr(query, "claim_text", str(query))
        else:
            query_text = str(query)

        if not query_text or not query_text.strip():
            return []

        # 1. Hybrid Retrieval (BM25 + Dense vector search + Min-Max normalization + Heading factor)
        candidates = self.hybrid_retriever.search(query_text, top_k=candidate_k)

        # 2. Multi-Feature Evidence Reranker
        reranked_results = self.reranker.rerank(query_text, candidates, top_k=top_k)

        # 3. Format structured evidence output with complete provenance
        evidence_list = []
        for item in reranked_results:
            # FIX 7: Remove fabricated fallback India Code URL; preserve actual source_url or ""
            source_url = item.get("source_url") or ""
            # FIX 6: Retrieval evidence default status is UNVERIFIED
            ver_status = item.get("verification_status") if item.get("verification_status") != "VERIFIED" else "UNVERIFIED"

            evidence_obj = {
                "claim": query_text,
                "rank": item.get("rank"),
                "chunk_id": item.get("chunk_id"),
                "document_id": item.get("document_id"),
                "document_type": item.get("document_type", "STATUTE"),
                "title": item.get("section_heading") or item.get("title", ""),
                "section_number": item.get("section_number"),
                "chapter_number": item.get("chapter_number"),
                "evidence_text": item.get("text", ""),
                "source_authority": item.get("source_authority", "India Code"),
                "source_url": source_url,
                "verification_status": ver_status,
                "bm25_score": item.get("bm25_raw_score", item.get("bm25_score", 0.0)),
                "dense_score": item.get("dense_raw_score", item.get("dense_score", 0.0)),
                "hybrid_score": item.get("hybrid_score", 0.0),
                "rerank_score": item.get("rerank_score", item.get("score", 0.0)),
                "features": item.get("features", {}),
            }
            evidence_list.append(evidence_obj)

        logger.info(f"Retrieved {len(evidence_list)} top evidence chunks for query: '{query_text[:50]}...'")
        return evidence_list

    def retrieve_evidence(self, claim: Claim) -> List[str]:
        """
        Backward-compatible helper returning a list of evidence text strings.
        """
        structured = self.retrieve(claim, top_k=3)
        return [item["evidence_text"] for item in structured]
