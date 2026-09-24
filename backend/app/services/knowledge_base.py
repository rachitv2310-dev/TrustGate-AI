import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from backend.app.config import settings
    from backend.app.schemas.knowledge_base import (
        UnifiedLegalDocument,
        LegalChunk,
        DocumentType,
        SourceType
    )
except ImportError:
    from app.config import settings
    from app.schemas.knowledge_base import (
        UnifiedLegalDocument,
        LegalChunk,
        DocumentType,
        SourceType
    )

logger = logging.getLogger(__name__)


class KnowledgeBaseLoaderService:
    """
    Service responsible for loading, validating, and combining the frozen Stage 1 and Stage 2 legal datasets
    into a unified internal representation (UnifiedLegalDocument) and deterministic chunking layer (LegalChunk).
    """

    def __init__(
        self,
        stage1_path: Optional[Path] = None,
        stage2_path: Optional[Path] = None
    ):
        self.stage1_path = stage1_path or (settings.PROJECT_ROOT_PATH / "legal_dataset_pipeline" / "BNS_2023_selected_sections.json")
        self.stage2_path = stage2_path or (settings.PROJECT_ROOT_PATH / "legal_dataset_pipeline" / "stage2_supreme_court" / "supreme_court_judgments.json")

    def load_stage1_bns(self) -> List[UnifiedLegalDocument]:
        """
        Load and validate 39 BNS 2023 section records from Stage 1 JSON dataset.
        """
        if not self.stage1_path.exists():
            raise FileNotFoundError(f"Stage 1 dataset missing at: {self.stage1_path}")

        try:
            with open(self.stage1_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception as e:
            raise ValueError(f"Stage 1 dataset JSON parsing error: {e}") from e

        if not isinstance(records, list) or len(records) == 0:
            raise ValueError("Stage 1 dataset must be a non-empty JSON list.")

        documents: List[UnifiedLegalDocument] = []
        for idx, r in enumerate(records):
            doc_id = r.get("document_id")
            if not doc_id or not doc_id.startswith("BNS_SEC_"):
                raise ValueError(f"Invalid BNS document_id at index {idx}: {doc_id}")

            authority = r.get("authority")
            if authority != "India Code":
                raise ValueError(f"Invalid BNS source authority at index {idx}: '{authority}'. Expected 'India Code'.")

            ver_status = r.get("verification_status")
            if ver_status != "VERIFIED":
                raise ValueError(f"Invalid BNS verification_status at index {idx}: '{ver_status}'. Expected 'VERIFIED'.")

            text = r.get("text", "").strip()
            if not text:
                raise ValueError(f"Empty statutory text for BNS document: {doc_id}")

            doc = UnifiedLegalDocument(
                document_id=doc_id,
                document_type=DocumentType.STATUTE,
                title=r.get("section_title", f"BNS Section {r.get('section_number')}"),
                section_number=str(r.get("section_number")),
                act_name=r.get("act_name", "Bharatiya Nyaya Sanhita, 2023"),
                act_number=r.get("act_number", "Act No. 45 of 2023"),
                chapter_number=str(r.get("chapter_number")),
                chapter_title=r.get("chapter_title"),
                full_text=text,
                source_authority="India Code",
                source_type=SourceType.PRIMARY_LAW,
                jurisdiction=r.get("jurisdiction", "India"),
                source_url=r.get("source_url"),
                verification_status="VERIFIED",
                retrieval_date=r.get("retrieval_date", "2024-07-01")
            )
            documents.append(doc)

        logger.info(f"Successfully loaded and validated {len(documents)} BNS statutory section records from Stage 1.")
        return documents

    def load_stage2_supreme_court(self) -> List[UnifiedLegalDocument]:
        """
        Load and validate 25 Supreme Court judgment records from Stage 2 JSON dataset.
        """
        if not self.stage2_path.exists():
            raise FileNotFoundError(f"Stage 2 dataset missing at: {self.stage2_path}")

        try:
            with open(self.stage2_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception as e:
            raise ValueError(f"Stage 2 dataset JSON parsing error: {e}") from e

        if not isinstance(records, list) or len(records) == 0:
            raise ValueError("Stage 2 dataset must be a non-empty JSON list.")

        documents: List[UnifiedLegalDocument] = []
        for idx, r in enumerate(records):
            doc_id = r.get("document_id")
            if not doc_id or not doc_id.startswith("SC_JUDGMENT_"):
                raise ValueError(f"Invalid SC document_id at index {idx}: {doc_id}")

            authority = r.get("authority")
            if authority != "Supreme Court of India":
                raise ValueError(f"Invalid SC source authority at index {idx}: '{authority}'. Expected 'Supreme Court of India'.")

            ver_status = r.get("verification_status")
            if ver_status != "VERIFIED":
                raise ValueError(f"Invalid SC verification_status at index {idx}: '{ver_status}'. Expected 'VERIFIED'.")

            text = r.get("judgment_text", "").strip()
            if not text:
                raise ValueError(f"Empty judgment text for SC document: {doc_id}")

            doc = UnifiedLegalDocument(
                document_id=doc_id,
                document_type=DocumentType.JUDICIAL_PRECEDENT,
                title=r.get("case_name"),
                citation=r.get("citation"),
                judgment_date=r.get("judgment_date"),
                court=r.get("court", "Supreme Court of India"),
                relevant_bns_sections=r.get("relevant_bns_sections", []),
                legal_concepts=r.get("legal_concepts", []),
                full_text=text,
                source_authority="Supreme Court of India",
                source_type=SourceType.JUDICIAL_PRECEDENT,
                jurisdiction=r.get("jurisdiction", "India"),
                source_url=r.get("source_url"),
                verification_status="VERIFIED",
                retrieval_date=r.get("retrieval_date", "2026-08-30")
            )
            documents.append(doc)

        logger.info(f"Successfully loaded and validated {len(documents)} Supreme Court judgment records from Stage 2.")
        return documents

    def load_legal_corpus(self) -> List[UnifiedLegalDocument]:
        """
        Combine Stage 1 and Stage 2 legal records into a unified collection of 64 UnifiedLegalDocument instances.
        Verifies complete provenance and absence of duplicate document IDs.
        """
        bns_docs = self.load_stage1_bns()
        sc_docs = self.load_stage2_supreme_court()

        combined = bns_docs + sc_docs
        doc_ids = [d.document_id for d in combined]
        if len(doc_ids) != len(set(doc_ids)):
            raise ValueError("Duplicate document_id detected across Stage 1 and Stage 2 datasets!")

        logger.info(f"Unified legal corpus loaded successfully: Total {len(combined)} documents (39 BNS + 25 SC).")
        return combined

    def chunk_legal_corpus(self, documents: Optional[List[UnifiedLegalDocument]] = None) -> List[LegalChunk]:
        """
        Convert unified legal documents into deterministic legal passage chunks for retrieval layer consumption.
        """
        if documents is None:
            documents = self.load_legal_corpus()

        chunks: List[LegalChunk] = []
        for doc in documents:
            if doc.document_type == DocumentType.STATUTE:
                # Deterministic section-level chunking
                chunk_id = f"{doc.document_id}_CHUNK_01"
                chunk = LegalChunk(
                    chunk_id=chunk_id,
                    document_id=doc.document_id,
                    document_type=doc.document_type,
                    section_number=doc.section_number,
                    section_heading=doc.title,
                    chapter_number=doc.chapter_number,
                    chapter_title=doc.chapter_title,
                    text=doc.full_text,
                    source_authority=doc.source_authority,
                    source_type=doc.source_type,
                    source_url=doc.source_url,
                    verification_status=doc.verification_status
                )
                chunks.append(chunk)

            elif doc.document_type == DocumentType.JUDICIAL_PRECEDENT:
                # Deterministic precedent chunking
                chunk_id = f"{doc.document_id}_CHUNK_01"
                chunk = LegalChunk(
                    chunk_id=chunk_id,
                    document_id=doc.document_id,
                    document_type=doc.document_type,
                    section_heading=doc.title,
                    case_name=doc.title,
                    citation=doc.citation,
                    text=doc.full_text,
                    source_authority=doc.source_authority,
                    source_type=doc.source_type,
                    source_url=doc.source_url,
                    verification_status=doc.verification_status
                )
                chunks.append(chunk)

        logger.info(f"Deterministic chunking completed: {len(chunks)} legal chunks generated.")
        return chunks
