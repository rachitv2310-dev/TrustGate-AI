from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    STATUTE = "STATUTE"
    JUDICIAL_PRECEDENT = "JUDICIAL_PRECEDENT"


class SourceType(str, Enum):
    PRIMARY_LAW = "Primary_Law"
    JUDICIAL_PRECEDENT = "Judicial_Precedent"


class UnifiedLegalDocument(BaseModel):
    """
    Unified Internal Representation for Legal Documents (BNS Statutes + SC Judgments).
    Preserves 100% of source provenance, authority, and statutory text.
    """
    document_id: str = Field(..., description="Unique document identifier, e.g. BNS_SEC_103 or SC_JUDGMENT_001")
    document_type: DocumentType = Field(..., description="STATUTE or JUDICIAL_PRECEDENT")
    title: str = Field(..., description="Section title or Case name")
    section_number: Optional[str] = Field(None, description="Statutory section number if applicable")
    act_name: Optional[str] = Field(None, description="Act name, e.g. Bharatiya Nyaya Sanhita, 2023")
    act_number: Optional[str] = Field(None, description="Act number, e.g. Act No. 45 of 2023")
    chapter_number: Optional[str] = Field(None, description="Chapter number if applicable")
    chapter_title: Optional[str] = Field(None, description="Chapter title if applicable")
    citation: Optional[str] = Field(None, description="Law report citation for judicial precedents")
    judgment_date: Optional[str] = Field(None, description="Date of judgment in YYYY-MM-DD format")
    court: Optional[str] = Field(None, description="Court authority name")
    relevant_bns_sections: List[str] = Field(default_factory=list, description="Mapped BNS section numbers")
    legal_concepts: List[str] = Field(default_factory=list, description="Primary legal concepts or keywords")
    full_text: str = Field(..., description="Exact, unparaphrased statutory or judgment text")
    source_authority: str = Field(..., description="India Code or Supreme Court of India")
    source_type: SourceType = Field(..., description="Primary_Law or Judicial_Precedent")
    jurisdiction: str = Field(default="India", description="Legal jurisdiction")
    source_url: str = Field(..., description="Authoritative source HTTPS URL")
    verification_status: str = Field(default="VERIFIED", description="Verification tag")
    retrieval_date: str = Field(..., description="Ingestion date in YYYY-MM-DD format")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to python dictionary."""
        return self.model_dump()


class LegalChunk(BaseModel):
    """
    Deterministic Legal Passage Chunk for Lexical & Dense Retrieval Adapters.
    """
    chunk_id: str = Field(..., description="Deterministic chunk identifier, e.g. BNS_SEC_103_CHUNK_01")
    document_id: str = Field(..., description="Parent document identifier")
    document_type: DocumentType = Field(..., description="STATUTE or JUDICIAL_PRECEDENT")
    section_number: Optional[str] = Field(None, description="Statutory section number")
    section_heading: Optional[str] = Field(None, description="Section heading or case name")
    case_name: Optional[str] = Field(None, description="Case name if judicial precedent")
    citation: Optional[str] = Field(None, description="Citation if judicial precedent")
    chapter_number: Optional[str] = Field(None, description="Chapter number")
    chapter_title: Optional[str] = Field(None, description="Chapter title")
    text: str = Field(..., description="Passage chunk text")
    source_authority: str = Field(..., description="India Code or Supreme Court of India")
    source_type: SourceType = Field(..., description="Primary_Law or Judicial_Precedent")
    source_url: str = Field(..., description="Source HTTPS URL")
    verification_status: str = Field(default="VERIFIED", description="Verification tag")

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk instance to python dictionary."""
        return self.model_dump()
