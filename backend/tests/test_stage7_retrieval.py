import sys
import unittest
from pathlib import Path

# Add backend and project root to sys.path
backend_dir = Path(__file__).resolve().parents[1]
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.app.schemas.claim import Claim
from backend.app.services.retriever import EvidenceRetrieverService


class TestStage7RetrievalStack(unittest.TestCase):
    """
    Stage 7 Retrieval Stack Test Suite.
    Validates BM25, Dense Semantic Retrieval, Min-Max Normalization, Heading Precision Factor,
    Multi-Feature Reranking, Provenance Preservation, and Top-3 Evidence Constraints.
    """

    @classmethod
    def setUpClass(cls):
        cls.retriever_service = EvidenceRetrieverService()

    def test_01_theft_section_303_query(self):
        """TEST 1: Query related to BNS Section 303 / Theft -> BNS Section 303 appears in Top-K."""
        query = "What is the punishment for theft under BNS Section 303?"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0, "No evidence retrieved for theft query!")
        self.assertLessEqual(len(results), 3, "Returned more than top_k=3 results!")
        
        # Verify Section 303 is in top evidence
        section_numbers = [str(r.get("section_number")) for r in results]
        self.assertIn("303", section_numbers, f"Section 303 not found in top evidence: {section_numbers}")
        
        top_result = results[0]
        self.assertEqual(top_result["document_id"], "BNS_2023")
        self.assertEqual(top_result["source_authority"], "India Code")

    def test_02_murder_section_103_query(self):
        """TEST 2: Query related to murder / Section 103 -> Relevant BNS murder evidence appears."""
        query = "What is the punishment for murder under Section 103 of BNS?"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        
        section_numbers = [str(r.get("section_number")) for r in results]
        self.assertIn("103", section_numbers, f"Section 103 not found in top evidence: {section_numbers}")
        
        top_result = results[0]
        self.assertTrue("murder" in top_result["title"].lower() or "murder" in top_result["evidence_text"].lower())

    def test_03_culpable_homicide_vs_murder_query(self):
        """TEST 3: Query related to culpable homicide vs murder -> Relevant BNS / SC precedent appears."""
        query = "What is the legal distinction between culpable homicide and murder?"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        
        # Check that top evidence covers Section 101 / Murder exceptions or SC precedents
        found_relevant = any(
            "101" in str(r.get("section_number")) or 
            "murder" in r.get("evidence_text", "").lower() or 
            "homicide" in r.get("evidence_text", "").lower()
            for r in results
        )
        self.assertTrue(found_relevant, "No relevant evidence for culpable homicide vs murder!")

    def test_04_criminal_conspiracy_query(self):
        """TEST 4: Query related to criminal conspiracy -> Section 61 or relevant SC precedent retrieved."""
        query = "What constitutes the offence of criminal conspiracy under Section 61?"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        
        section_numbers = [str(r.get("section_number")) for r in results]
        self.assertIn("61", section_numbers, f"Section 61 not found in top evidence: {section_numbers}")

    def test_05_semantic_variation_query(self):
        """TEST 5: Query semantically different from exact statutory wording -> Dense retrieval contributes candidates."""
        query = "taking someone else's movable property without their consent dishonestly"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        
        # Verify theft section 303 or related property offence is retrieved
        retrieved_texts = " ".join([r.get("evidence_text", "").lower() for r in results])
        self.assertTrue(any(term in retrieved_texts for term in ["movable", "property", "theft", "stolen"]))

    def test_06_provenance_field_validation(self):
        """TEST 6: Verify provenance - every result has document_id, evidence_text, source_authority, source_url."""
        query = "cheating and dishonestly inducing delivery of property"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        
        for item in results:
            self.assertTrue(bool(item.get("document_id")), "Missing document_id in evidence!")
            self.assertTrue(bool(item.get("evidence_text", "").strip()), "Missing evidence_text!")
            self.assertTrue(bool(item.get("source_authority")), "Missing source_authority!")
            self.assertIsInstance(item.get("source_url"), str, "source_url must be a string!")
            self.assertIn(item.get("verification_status"), ["UNVERIFIED", "VERIFIED"], "Verification status is not valid!")

    def test_07_top_k_constraint(self):
        """TEST 7: Verify Top-K - Reranker returns no more than 3 final evidence chunks."""
        query = "punishment for offenses against property"
        results = self.retriever_service.retrieve(query, top_k=3)
        self.assertLessEqual(len(results), 3, "Reranker returned more than 3 evidence chunks!")

    def test_08_deterministic_behavior(self):
        """TEST 8: Verify deterministic behavior - identical queries produce identical rankings and scores."""
        query = "What is criminal intimidation under BNS Section 351?"
        results_1 = self.retriever_service.retrieve(query, top_k=3)
        results_2 = self.retriever_service.retrieve(query, top_k=3)
        
        self.assertEqual(len(results_1), len(results_2))
        for r1, r2 in zip(results_1, results_2):
            self.assertEqual(r1["chunk_id"], r2["chunk_id"])
            self.assertEqual(r1["rerank_score"], r2["rerank_score"])

    def test_09_backward_compatibility(self):
        """TEST 9: Verify backward-compatible retrieve_evidence(claim) returns List[str]."""
        claim = Claim(id="CLAIM_001", text="Section 103 prescribes punishment for murder.")
        evidence_strings = self.retriever_service.retrieve_evidence(claim)
        self.assertIsInstance(evidence_strings, list)
        self.assertGreater(len(evidence_strings), 0)
        self.assertIsInstance(evidence_strings[0], str)


if __name__ == "__main__":
    unittest.main()
