from fastapi import APIRouter
from backend.app.services.retriever import EvidenceRetrieverService

router = APIRouter(prefix="/retrieval-test", tags=["Stage 7 Retrieval"])

retriever = EvidenceRetrieverService()


@router.get("/")
async def test_retrieval(
    query: str = "What is the punishment for theft under Section 303 of the Bharatiya Nyaya Sanhita?",
    top_k: int = 3,
):
    results = retriever.retrieve(query, top_k=top_k)

    return {
        "query": query,
        "total_results": len(results),
        "retrieval_method": "BM25 + Dense Hybrid Retrieval + Multi-Feature Reranking",
        "results": results,
    }
