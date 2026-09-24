import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from backend.app.retrieval.hybrid_retriever import HybridRetriever
    from backend.app.services.retriever import EvidenceRetrieverService
except ImportError:
    from app.retrieval.hybrid_retriever import HybridRetriever
    from app.services.retriever import EvidenceRetrieverService


TEST_CASES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "question": "What is theft under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Theft is defined under Section 303 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "303",
        "expected_description": "Theft"
    },
    {
        "id": 2,
        "question": "What is robbery under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Robbery is defined under Section 309 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "309",
        "expected_description": "Robbery"
    },
    {
        "id": 3,
        "question": "When does theft become robbery under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Theft becomes robbery under Section 309 of the Bharatiya Nyaya Sanhita, 2023 when hurt or restraint is caused.",
        "expected_section": "309",
        "expected_description": "Theft vs Robbery"
    },
    {
        "id": 4,
        "question": "What is dacoity under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Dacoity is defined under Section 310 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "310",
        "expected_description": "Dacoity"
    },
    {
        "id": 5,
        "question": "What is the punishment for dacoity under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Punishment for dacoity is specified under Section 310 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "310",
        "expected_description": "Punishment for Dacoity"
    },
    {
        "id": 6,
        "question": "What is criminal breach of trust under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Criminal breach of trust is defined under Section 316 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "316",
        "expected_description": "Criminal Breach of Trust"
    },
    {
        "id": 7,
        "question": "What constitutes cheating under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Cheating is defined under Section 318 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "318",
        "expected_description": "Cheating"
    },
    {
        "id": 8,
        "question": "What is making a false document under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Making a false document is defined under Section 335 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "335",
        "expected_description": "False Document"
    },
    {
        "id": 9,
        "question": "What is forgery under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Forgery is defined under Section 336 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "336",
        "expected_description": "Forgery"
    },
    {
        "id": 10,
        "question": "What is the punishment for forgery under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Punishment for forgery is specified under Section 336 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "336",
        "expected_description": "Punishment for Forgery"
    },
    {
        "id": 11,
        "question": "What is criminal intimidation under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Criminal intimidation is defined under Section 351 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "351",
        "expected_description": "Criminal Intimidation"
    },
    {
        "id": 12,
        "question": "What is defamation under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Defamation is defined under Section 356 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "356",
        "expected_description": "Defamation"
    },
    {
        "id": 13,
        "question": "What is kidnapping under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Kidnapping is defined under Section 137 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "137",
        "expected_description": "Kidnapping"
    },
    {
        "id": 14,
        "question": "What is abduction under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Abduction is defined under Section 138 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "138",
        "expected_description": "Abduction"
    },
    {
        "id": 15,
        "question": "What is murder under the Bharatiya Nyaya Sanhita, 2023?",
        "ai_response": "Murder is defined under Section 101 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_section": "101",
        "expected_description": "Murder"
    }
]


def normalize_sec(sec_val: Any) -> str:
    """Robust normalization of section numbers to standard strings."""
    if sec_val is None:
        return ""
    s = str(sec_val).strip()
    s = re.sub(r"^(?:section|sec\.?)\s*", "", s, flags=re.IGNORECASE)
    s = s.strip(" .(),")
    return s


def evaluate_retrieval():
    print("=" * 110)
    print("TRUSTGATE-AI 15-CASE RETRIEVAL ACCURACY EVALUATION")
    print("Evaluation Mode: Legal Semantic Embedding (shb/legal-embed) + BM25 Hybrid Retrieval")
    print("Retrieval Entry Point: EvidenceRetrieverService.retrieve(query, top_k=5)")
    print("Retrieval Input Used: Question text")
    print("=" * 110)

    # Initialize production legal hybrid retrieval service
    legal_hybrid = HybridRetriever(semantic_backend="legal_embed")
    service = EvidenceRetrieverService(hybrid_retriever=legal_hybrid)

    r1_correct = 0
    r3_correct = 0
    r5_correct = 0

    failed_cases = []

    print(f"{'ID':<3} | {'Expected':<8} | {'Top 1':<8} | {'Top 3 Sections':<25} | {'Top 5 Sections':<35} | {'R@1':<3} | {'R@3':<3} | {'R@5':<3}")
    print("-" * 110)

    for item in TEST_CASES:
        case_id = item["id"]
        query = item["question"]
        expected_sec = normalize_sec(item["expected_section"])

        # Execute actual production retrieval service
        results = service.retrieve(query, top_k=5)

        retrieved_secs = [normalize_sec(r.get("section_number")) for r in results]
        top1 = retrieved_secs[0] if retrieved_secs else "NONE"
        top3 = retrieved_secs[:3]
        top5 = retrieved_secs[:5]

        r1_pass = (expected_sec == top1)
        r3_pass = (expected_sec in top3)
        r5_pass = (expected_sec in top5)

        if r1_pass:
            r1_correct += 1
        else:
            failed_cases.append({
                "id": case_id,
                "description": item["expected_description"],
                "question": query,
                "expected": expected_sec,
                "top1": top1,
                "top3": top3,
                "top5": top5,
                "top1_title": results[0].get("title") if results else "N/A"
            })

        if r3_pass:
            r3_correct += 1
        if r5_pass:
            r5_correct += 1

        top3_str = ", ".join(top3)
        top5_str = ", ".join(top5)
        r1_str = "1" if r1_pass else "0"
        r3_str = "1" if r3_pass else "0"
        r5_str = "1" if r5_pass else "0"

        print(f"{case_id:02d} | {expected_sec:<8} | {top1:<8} | {top3_str:<25} | {top5_str:<35} | {r1_str:<3} | {r3_str:<3} | {r5_str:<3}")

    print("-" * 110)

    total = len(TEST_CASES)
    r1_pct = (r1_correct / total) * 100
    r3_pct = (r3_correct / total) * 100
    r5_pct = (r5_correct / total) * 100

    print("\nRetrieval Accuracy Summary")
    print(f"Recall@1: {r1_correct}/{total} = {r1_pct:.1f}%")
    print(f"Recall@3: {r3_correct}/{total} = {r3_pct:.1f}%")
    print(f"Recall@5: {r5_correct}/{total} = {r5_pct:.1f}%")

    if failed_cases:
        print("\nFailed Cases at Recall@1:")
        for fc in failed_cases:
            print(f"- Case {fc['id']:02d} ({fc['description']}): Expected Section {fc['expected']}, but Top-1 was Section {fc['top1']} (Heading: '{fc['top1_title']}')")
            print(f"  Query: '{fc['question']}'")
            print(f"  Returned Top-5 Sections: {fc['top5']}\n")
    else:
        print("\nNo failures at Recall@1! All 15 cases passed perfectly!")


if __name__ == "__main__":
    evaluate_retrieval()
