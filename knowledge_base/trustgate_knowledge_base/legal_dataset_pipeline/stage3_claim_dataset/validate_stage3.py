import json
import sys
from pathlib import Path

def validate():
    base_dir = Path(__file__).resolve().parent
    dataset_file = base_dir / "stage3_claim_verification_dataset.json"
    manifest_file = base_dir / "stage3_dataset_manifest.json"

    assert dataset_file.exists(), f"Missing {dataset_file}"
    assert manifest_file.exists(), f"Missing {manifest_file}"

    with open(dataset_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    assert 100 <= len(records) <= 150, f"Expected 100-150 records, got {len(records)}"

    rec_ids = set()
    claim_ids = set()
    valid_labels = {"SUPPORTED", "REFUTED", "INSUFFICIENT"}

    for r in records:
        assert r["record_id"] not in rec_ids
        assert r["claim_id"] not in claim_ids
        assert r["verification_label"] in valid_labels
        assert len(r["claim"].strip()) > 5
        assert len(r["evidence_text"].strip()) > 10
        assert r["source_url"].startswith("http")
        rec_ids.add(r["record_id"])
        claim_ids.add(r["claim_id"])

    print(f"STAGE 3 VALIDATION PASSED 100%! All {len(records)} records verified.")

if __name__ == "__main__":
    validate()
