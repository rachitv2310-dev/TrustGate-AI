import json
import sys
from pathlib import Path

def validate():
    base_dir = Path(__file__).resolve().parent
    stats_file = base_dir / "stage4_dataset_statistics.json"
    flags_file = base_dir / "stage4_quality_flags.json"
    cov_file = base_dir / "stage4_evidence_coverage.json"
    report_file = base_dir / "stage4_evaluation_report.md"

    for fpath in [stats_file, flags_file, cov_file, report_file]:
        assert fpath.exists(), f"Missing required deliverable {fpath}"

    with open(stats_file, "r", encoding="utf-8") as f:
        stats = json.load(f)

    assert stats["total_stage3_records"] == 120
    assert stats["overall_integrity_score"] == "100.0%"
    assert stats["flagged_record_count"] == 0

    print("STAGE 4 EVALUATION & READINESS VALIDATION PASSED 100%!")

if __name__ == "__main__":
    validate()
