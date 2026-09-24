import sys
import unittest
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parents[1]
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.app.schemas.knowledge_base import (
    UnifiedLegalDocument,
    LegalChunk,
    DocumentType,
    SourceType
)
from backend.app.services.knowledge_base import KnowledgeBaseLoaderService
from backend.app.retrieval.vector_store import VectorStoreInterface


class TestStage6KnowledgeBaseIntegration(unittest.TestCase):
    """
    12-Point Test Suite for Stage 6 Knowledge Base Integration.
    """

    @classmethod
    def setUpClass(cls):
        cls.kb_service = KnowledgeBaseLoaderService()
        cls.stage1_path = cls.kb_service.stage1_path
        cls.stage2_path = cls.kb_service.stage2_path

    def test_01_stage1_bns_loading(self):
        """1. Validate Stage 1 dataset loading (39 BNS sections)."""
        bns_docs = self.kb_service.load_stage1_bns()
        self.assertEqual(len(bns_docs), 39, f"Expected 39 BNS sections, got {len(bns_docs)}")
        for doc in bns_docs:
            self.assertEqual(doc.document_type, DocumentType.STATUTE)
            self.assertEqual(doc.source_type, SourceType.PRIMARY_LAW)
            self.assertEqual(doc.source_authority, "India Code")

    def test_02_stage2_supreme_court_loading(self):
        """2. Validate Stage 2 dataset loading (25 SC judgments)."""
        sc_docs = self.kb_service.load_stage2_supreme_court()
        self.assertEqual(len(sc_docs), 25, f"Expected 25 SC judgments, got {len(sc_docs)}")
        for doc in sc_docs:
            self.assertEqual(doc.document_type, DocumentType.JUDICIAL_PRECEDENT)
            self.assertEqual(doc.source_type, SourceType.JUDICIAL_PRECEDENT)
            self.assertEqual(doc.source_authority, "Supreme Court of India")

    def test_03_combined_corpus_count(self):
        """3. Validate combined corpus count equals exactly 64 legal documents."""
        corpus = self.kb_service.load_legal_corpus()
        self.assertEqual(len(corpus), 64, f"Expected 64 total legal documents, got {len(corpus)}")

    def test_04_all_bns_documents_present(self):
        """4. Validate all 39 Stage 1 BNS section documents are present."""
        corpus = self.kb_service.load_legal_corpus()
        bns_ids = {d.document_id for d in corpus if d.document_type == DocumentType.STATUTE}
        self.assertEqual(len(bns_ids), 39)
        self.assertTrue(all(doc_id.startswith("BNS_SEC_") for doc_id in bns_ids))

    def test_05_all_sc_documents_present(self):
        """5. Validate all 25 Stage 2 Supreme Court documents are present."""
        corpus = self.kb_service.load_legal_corpus()
        sc_ids = {d.document_id for d in corpus if d.document_type == DocumentType.JUDICIAL_PRECEDENT}
        self.assertEqual(len(sc_ids), 25)
        self.assertTrue(all(doc_id.startswith("SC_JUDGMENT_") for doc_id in sc_ids))

    def test_06_no_duplicate_document_ids(self):
        """6. Validate no duplicate document IDs exist in the combined corpus."""
        corpus = self.kb_service.load_legal_corpus()
        doc_ids = [d.document_id for d in corpus]
        self.assertEqual(len(doc_ids), len(set(doc_ids)), "Duplicate document IDs found in unified corpus!")

    def test_07_required_provenance_fields_exist(self):
        """7. Validate required provenance fields exist across all documents."""
        corpus = self.kb_service.load_legal_corpus()
        for doc in corpus:
            self.assertTrue(bool(doc.document_id.strip()))
            self.assertTrue(bool(doc.title.strip()))
            self.assertTrue(bool(doc.source_authority.strip()))
            self.assertTrue(doc.source_url.startswith("http"))
            self.assertTrue(bool(doc.retrieval_date.strip()))
            self.assertEqual(doc.jurisdiction, "India")

    def test_08_source_authority_preserved(self):
        """8. Validate source authority is accurately preserved."""
        corpus = self.kb_service.load_legal_corpus()
        for doc in corpus:
            if doc.document_type == DocumentType.STATUTE:
                self.assertEqual(doc.source_authority, "India Code")
            elif doc.document_type == DocumentType.JUDICIAL_PRECEDENT:
                self.assertEqual(doc.source_authority, "Supreme Court of India")

    def test_09_verification_status_preserved(self):
        """9. Validate verification status tag is preserved as VERIFIED."""
        corpus = self.kb_service.load_legal_corpus()
        for doc in corpus:
            self.assertEqual(doc.verification_status, "VERIFIED")

    def test_10_source_text_non_empty(self):
        """10. Validate statutory and judgment source texts are non-empty (>50 chars)."""
        corpus = self.kb_service.load_legal_corpus()
        for doc in corpus:
            self.assertGreater(len(doc.full_text.strip()), 50, f"Source text for {doc.document_id} is too short")

    def test_11_frozen_source_files_unchanged(self):
        """11. Assert frozen Stage 1 & Stage 2 source files exist and remain untouched."""
        self.assertTrue(self.stage1_path.exists(), "Stage 1 source file missing!")
        self.assertTrue(self.stage2_path.exists(), "Stage 2 source file missing!")

    def test_12_unified_corpus_consumed_by_vector_store(self):
        """12. Validate unified corpus can be consumed directly by VectorStoreInterface."""
        vector_store = VectorStoreInterface(use_kb_service=True)
        chunks = vector_store.get_all_chunks()
        self.assertEqual(len(chunks), 64, f"Expected VectorStore to load 64 chunks from KB service, got {len(chunks)}")
        
        # Test lookup by chunk_id
        sample_chunk = vector_store.get_chunk("BNS_SEC_103_CHUNK_01")
        self.assertIsNotNone(sample_chunk)
        self.assertEqual(sample_chunk["source_authority"], "India Code")

        sample_sc_chunk = vector_store.get_chunk("SC_JUDGMENT_001_CHUNK_01")
        self.assertIsNotNone(sample_sc_chunk)
        self.assertEqual(sample_sc_chunk["source_authority"], "Supreme Court of India")


if __name__ == "__main__":
    unittest.main()
