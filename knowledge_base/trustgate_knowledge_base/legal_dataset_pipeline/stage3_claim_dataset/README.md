# Stage 3 — Legal Claim & Verification Dataset Pipeline

This module constructs, validates, and stores structured legal claim-verification benchmark records for testing TrustGate AI's verification pipeline.

## Directory Structure
```
legal_dataset_pipeline/stage3_claim_dataset/
│
├── stage3_claim_verification_dataset.json  # Structured dataset of 120 claim-verification records
├── stage3_dataset_manifest.json            # Dataset provenance and metric manifest
├── stage3_collection_report.md            # Comprehensive Stage 3 report
├── build_stage3_dataset.py                 # Pipeline builder script
├── validate_stage3.py                      # 14-point automated validation engine
└── README.md                              # Technical documentation
```

## Running Validation
To execute the automated 14-point validation engine:
```bash
python legal_dataset_pipeline/stage3_claim_dataset/validate_stage3.py
```
