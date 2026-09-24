import json
import re
import sys
from pathlib import Path

def validate():
    base_dir = Path(__file__).resolve().parents[1]
    j_file = base_dir / "supreme_court_judgments.json"
    m_file = base_dir / "supreme_court_source_manifest.json"

    assert j_file.exists(), f"Missing {j_file}"
    assert m_file.exists(), f"Missing {m_file}"

    with open(j_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 25, f"Expected 25 records, got {len(data)}"
    doc_ids = set()
    case_names = set()

    for d in data:
        assert d["court"] == "Supreme Court of India"
        assert d["authority"] == "Supreme Court of India"
        assert d["jurisdiction"] == "India"
        assert d["source_type"] == "Judicial_Precedent"
        assert d["verification_status"] == "VERIFIED"
        assert d["document_id"] not in doc_ids
        assert d["case_name"] not in case_names
        assert len(d["judgment_text"].strip()) > 50
        assert d["source_url"].startswith("http")
        doc_ids.add(d["document_id"])
        case_names.add(d["case_name"])

    print("STAGE 2 SUPREME COURT VALIDATION PASSED 100%! All 25 judgments verified.")

if __name__ == "__main__":
    validate()
