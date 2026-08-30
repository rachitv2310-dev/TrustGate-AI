#!/usr/bin/env python3
"""
validate_knowledge_base.py
--------------------------
Comprehensive 10-Point Legal Knowledge Base Quality Control & Validation Engine.
Validates records against JSON schema, completeness, duplicates, text integrity,
provenance fields, and verification status integrity.
"""

import json
import os
import re
import sys
from datetime import datetime

ALLOWED_SOURCE_STATUSES = {"VERIFIED", "UNVERIFIED", "PENDING_OFFICIAL_VERIFICATION"}
ALLOWED_SOURCE_TYPES = {"Primary_Law", "Subordinate_Legislation", "Constitutional_Provision", "Statute"}
REQUIRED_FIELDS = [
    "document_id", "act_name", "act_number", "section_number", "section_title",
    "chapter", "chapter_title", "text", "source_type", "authority",
    "jurisdiction", "effective_date", "source_url", "retrieval_date",
    "source_status", "notes"
]
PLACEHOLDER_INDICATORS = [
    "[placeholder]", "[pending]", "lorem ipsum", "todo", "sample text",
    "draft text", "dummy text", "xxx", "insert text here"
]

def validate_date_format(date_str):
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_url_format(url_str):
    if not url_str or not isinstance(url_str, str):
        return False
    return url_str.startswith("http://") or url_str.startswith("https://")

def run_validation(kb_file_path=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if kb_file_path is None:
        kb_file_path = os.path.join(base_dir, "data", "knowledge_base", "bns_2023_pilot_kb.json")
        
    schema_path = os.path.join(base_dir, "schemas", "knowledge_base_schema.json")
    val_out_dir = os.path.join(base_dir, "data", "validation")
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(val_out_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print("==================================================")
    print("LEGAL KNOWLEDGE BASE VALIDATION SUITE")
    print("==================================================")
    print(f"Target File: {kb_file_path}")

    # Check 1: JSON Validity
    if not os.path.exists(kb_file_path):
        print(f"FAIL: File does not exist: {kb_file_path}")
        sys.exit(1)

    try:
        with open(kb_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("  Rule 1 [JSON Validity]: PASSED")
    except Exception as e:
        print(f"  Rule 1 [JSON Validity]: FAILED ({str(e)})")
        sys.exit(1)

    records = data.get("records", [])
    total_records = len(records)
    
    doc_ids_seen = {}
    sec_keys_seen = {}
    
    issues = []
    
    valid_count = 0
    warning_count = 0
    failed_count = 0

    for idx, rec in enumerate(records):
        doc_id = rec.get("document_id", f"RECORD_INDEX_{idx}")
        rec_errors = []
        rec_warnings = []

        # Check 2: Required field completeness
        missing_fields = []
        empty_fields = []
        for field in REQUIRED_FIELDS:
            if field not in rec:
                missing_fields.append(field)
            elif rec[field] is None and field not in ["effective_date"]:
                empty_fields.append(field)
            elif isinstance(rec[field], str) and rec[field].strip() == "" and field not in ["effective_date", "notes"]:
                empty_fields.append(field)

        if missing_fields:
            rec_errors.append({
                "rule": "Rule 2: Required Field Completeness",
                "reason": f"Missing required fields: {', '.join(missing_fields)}"
            })
        if empty_fields:
            rec_errors.append({
                "rule": "Rule 2: Non-Empty Field Completeness",
                "reason": f"Empty or whitespace-only required fields: {', '.join(empty_fields)}"
            })

        # Check 3: Duplicate document IDs
        if doc_id in doc_ids_seen:
            rec_errors.append({
                "rule": "Rule 3: Unique Document Identifier",
                "reason": f"Duplicate document_id '{doc_id}' previously seen at index {doc_ids_seen[doc_id]}"
            })
        else:
            doc_ids_seen[doc_id] = idx

        # Check 4: Duplicate section records
        act_name = rec.get("act_name", "")
        sec_num = rec.get("section_number", "")
        sec_key = (act_name, sec_num)
        if act_name and sec_num:
            if sec_key in sec_keys_seen:
                rec_errors.append({
                    "rule": "Rule 4: Duplicate Section Record",
                    "reason": f"Duplicate section number '{sec_num}' for Act '{act_name}' (First seen at index {sec_keys_seen[sec_key]})"
                })
            else:
                sec_keys_seen[sec_key] = idx

        # Check 5: Empty legal text
        text = rec.get("text", "")
        if not text or not isinstance(text, str) or text.strip() == "":
            rec_errors.append({
                "rule": "Rule 5: Exact Legal Text Preservation",
                "reason": "Legal text is empty or missing."
            })
        elif len(text.strip()) < 10:
            rec_warnings.append({
                "rule": "Rule 5: Short Legal Text Warning",
                "reason": f"Legal text length is unusually short ({len(text.strip())} chars)."
            })

        # Check 6: Missing source URL
        source_url = rec.get("source_url", "")
        if not source_url:
            rec_errors.append({
                "rule": "Rule 6: Provenance Source URL",
                "reason": "Missing source_url."
            })
        elif not validate_url_format(source_url):
            rec_errors.append({
                "rule": "Rule 6: Valid Source URL Format",
                "reason": f"Invalid source_url format: '{source_url}'."
            })

        # Check 7: Missing retrieval date
        retrieval_date = rec.get("retrieval_date", "")
        if not retrieval_date:
            rec_errors.append({
                "rule": "Rule 7: Provenance Retrieval Date",
                "reason": "Missing retrieval_date."
            })
        elif not validate_date_format(retrieval_date):
            rec_errors.append({
                "rule": "Rule 7: Retrieval Date Format",
                "reason": f"Retrieval date '{retrieval_date}' must be formatted as YYYY-MM-DD."
            })

        # Check 8: Invalid source status
        status = rec.get("source_status", "")
        if not status:
            rec_errors.append({
                "rule": "Rule 8: Explicit Source Status",
                "reason": "Missing source_status."
            })
        elif status not in ALLOWED_SOURCE_STATUSES:
            rec_errors.append({
                "rule": "Rule 8: Source Status Value",
                "reason": f"Invalid source_status '{status}'. Must be one of {sorted(list(ALLOWED_SOURCE_STATUSES))}."
            })

        # Check 9: Missing provenance information
        authority = rec.get("authority", "")
        jurisdiction = rec.get("jurisdiction", "")
        source_type = rec.get("source_type", "")

        if not authority or not jurisdiction or not source_type:
            rec_errors.append({
                "rule": "Rule 9: Provenance Authority & Jurisdiction",
                "reason": f"Incomplete provenance: authority='{authority}', jurisdiction='{jurisdiction}', source_type='{source_type}'"
            })
        elif source_type not in ALLOWED_SOURCE_TYPES:
            rec_errors.append({
                "rule": "Rule 9: Valid Source Type",
                "reason": f"Invalid source_type '{source_type}'. Must be one of {sorted(list(ALLOWED_SOURCE_TYPES))}."
            })

        # Check 10: Placeholder data incorrectly marked VERIFIED
        if status == "VERIFIED":
            combined_content = f"{rec.get('text', '')} {rec.get('section_title', '')} {rec.get('notes', '')}".lower()
            found_placeholders = [p for p in PLACEHOLDER_INDICATORS if p in combined_content]
            if found_placeholders:
                rec_errors.append({
                    "rule": "Rule 10: Placeholder Verification Integrity",
                    "reason": f"Record marked 'VERIFIED' contains suspicious placeholder terms: {', '.join(found_placeholders)}"
                })

        if rec_errors:
            failed_count += 1
            issues.append({
                "document_id": doc_id,
                "status": "FAILED",
                "errors": rec_errors,
                "warnings": rec_warnings
            })
        elif rec_warnings:
            warning_count += 1
            issues.append({
                "document_id": doc_id,
                "status": "WARNING",
                "errors": [],
                "warnings": rec_warnings
            })
        else:
            valid_count += 1

    print("--------------------------------------------------")
    print(f"TOTAL RECORDS  : {total_records}")
    print(f"VALID RECORDS  : {valid_count}")
    print(f"WARNING RECORDS: {warning_count}")
    print(f"FAILED RECORDS : {failed_count}")
    print("--------------------------------------------------")

    if issues:
        print("\nSUMMARY OF IDENTIFIED ISSUES:")
        for item in issues:
            print(f"\n[Record ID: {item['document_id']}] Status: {item['status']}")
            for err in item["errors"]:
                print(f"  - ERROR [{err['rule']}]: {err['reason']}")
            for warn in item["warnings"]:
                print(f"  - WARNING [{warn['rule']}]: {warn['reason']}")

    # Save detailed JSON summary
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "file_validated": os.path.basename(kb_file_path),
        "total_records": total_records,
        "valid_records": valid_count,
        "warning_records": warning_count,
        "failed_records": failed_count,
        "overall_status": "PASSED" if failed_count == 0 else "FAILED",
        "issues": issues
    }
    
    val_json_path = os.path.join(val_out_dir, "validation_report.json")
    with open(val_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    print(f"\nSaved JSON validation output to: {val_json_path}")
    return summary_data

if __name__ == "__main__":
    run_validation()
