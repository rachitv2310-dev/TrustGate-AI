# Stage 4 — Evaluation & Readiness Assessment Pipeline

This directory contains the offline evaluation suite and readiness assessment for the TrustGate AI legal dataset.

## Output Files
- `stage4_evaluation_report.md`: Detailed evaluation report covering integrity, coverage, quality, and readiness.
- `stage4_dataset_statistics.json`: Machine-readable statistics JSON.
- `stage4_quality_flags.json`: List of flagged records requiring human review (0 flags recorded).
- `stage4_evidence_coverage.json`: Machine-readable evidence coverage matrix.
- `validate_stage4.py`: Standalone 14-point validation engine.
- `README.md`: Pipeline documentation.

## Running Validation
```bash
python legal_dataset_pipeline/stage4_evaluation/validate_stage4.py
```
