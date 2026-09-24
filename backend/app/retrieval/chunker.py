import re
from typing import List, Dict, Any, Optional


class DocumentChunker:
    """
    Domain-specific legal text chunking utilities for statutory documents (e.g., BNS 2023).
    Enforces ONE LEGAL SECTION = ONE RETRIEVAL UNIT wherever practical, preserving section_number
    and heading metadata while allowing sub-chunking for unusually large sections.
    """

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split raw text into overlapping passage chunks.
        """
        if not text or not text.strip():
            return []

        words = text.split()
        if len(words) <= chunk_size:
            return [text.strip()]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_str = " ".join(words[start:end])
            chunks.append(chunk_str)
            if end == len(words):
                break
            start += (chunk_size - overlap)

        return chunks

    def chunk_section(
        self,
        doc_id: str,
        section_number: str,
        section_heading: str,
        text: str,
        chapter_number: str = "",
        chapter_title: str = "",
        max_words: int = 400,
    ) -> List[Dict[str, Any]]:
        """
        Produce section-aware legal chunk dictionaries preserving section metadata and JSONL schema.
        """
        cleaned_text = re.sub(r"\s+", " ", text.strip())
        words = cleaned_text.split()

        if len(words) <= max_words:
            chunk_id = f"{doc_id}_SEC{section_number}_CHUNK01" if section_number else f"{doc_id}_CHUNK01"
            return [{
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "section_number": section_number,
                "section_heading": section_heading,
                "chunk_index": 1,
                "total_chunks_in_section": 1,
                "text": cleaned_text,
            }]

        # Sub-chunk large sections logically
        sub_texts = self.chunk_text(cleaned_text, chunk_size=max_words, overlap=50)
        chunks = []
        total_sub = len(sub_texts)

        for idx, sub_t in enumerate(sub_texts, 1):
            chunk_id = f"{doc_id}_SEC{section_number}_CHUNK{idx:02d}" if section_number else f"{doc_id}_CHUNK{idx:02d}"
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "section_number": section_number,
                "section_heading": section_heading,
                "chunk_index": idx,
                "total_chunks_in_section": total_sub,
                "text": sub_t,
            })

        return chunks
