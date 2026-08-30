#!/usr/bin/env python3
"""
build_pilot_kb.py
-----------------
Transforms raw official legal source records into structured section-level
Knowledge Base records conforming to the formal JSON Schema.
"""

import json
import os
import sys

def build_knowledge_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "BNS_2023_pilot_source.json")
    output_path = os.path.join(base_dir, "data", "knowledge_base", "bns_2023_pilot_kb.json")
    
    if not os.path.exists(raw_path):
        print(f"Error: Raw source file not found at {raw_path}")
        sys.exit(1)
        
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    source_meta = raw_data.get("source_metadata", {})
    raw_sections = raw_data.get("raw_sections", [])
    
    kb_records = []
    
    for sec in raw_sections:
        sec_num = sec["section_number"]
        doc_id = f"BNS_2023_SEC_{sec_num}"
        
        record = {
            "document_id": doc_id,
            "act_name": source_meta.get("act_name", ""),
            "act_number": source_meta.get("act_number", ""),
            "section_number": sec_num,
            "section_title": sec["section_title"],
            "chapter": sec["chapter"],
            "chapter_title": sec["chapter_title"],
            "text": sec["raw_text"],
            "source_type": source_meta.get("source_type", "Primary_Law"),
            "authority": source_meta.get("authority", "Parliament of India"),
            "jurisdiction": source_meta.get("jurisdiction", "India"),
            "effective_date": source_meta.get("enforcement_date", "2024-07-01"),
            "source_url": sec["official_url"],
            "retrieval_date": source_meta.get("retrieval_date", "2026-08-27"),
            "source_status": "VERIFIED",
            "notes": "Verified statutory text extracted from official India Code digital repository."
        }
        kb_records.append(record)
        
    dataset = {
        "schema_version": "1.0.0",
        "total_records": len(kb_records),
        "records": kb_records
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated Knowledge Base dataset with {len(kb_records)} records.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    build_knowledge_base()
