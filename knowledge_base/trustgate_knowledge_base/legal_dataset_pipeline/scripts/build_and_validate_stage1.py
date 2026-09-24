import json
from pathlib import Path

def validate():
    base_dir = Path(__file__).resolve().parents[1]
    sec_file = base_dir / "BNS_2023_selected_sections.json"
    man_file = base_dir / "BNS_2023_source_manifest.json"

    assert sec_file.exists(), f"Missing {sec_file}"
    assert man_file.exists(), f"Missing {man_file}"

    with open(sec_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    assert len(records) == 39, f"Expected 39 records, got {len(records)}"
    doc_ids = set()
    sec_nums = set()

    for r in records:
        assert r["act_name"] == "Bharatiya Nyaya Sanhita, 2023"
        assert r["act_number"] == "45 of 2023"
        assert r["authority"] == "India Code"
        assert r["jurisdiction"] == "India"
        assert r["verification_status"] == "VERIFIED"
        assert r["document_id"] not in doc_ids
        assert r["section_number"] not in sec_nums
        assert len(r["text"].strip()) > 10
        doc_ids.add(r["document_id"])
        sec_nums.add(r["section_number"])

    print("STAGE 1 VALIDATION PASSED 100%! All 39 records verified.")

if __name__ == "__main__":
    validate()
