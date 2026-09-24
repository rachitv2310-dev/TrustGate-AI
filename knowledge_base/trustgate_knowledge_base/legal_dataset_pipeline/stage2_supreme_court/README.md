# Stage 2 — Supreme Court Judgment Dataset Pipeline

This module constructs, validates, and stores structured landmark judicial precedent records from the Supreme Court of India linked to the Bharatiya Nyaya Sanhita, 2023 (BNS).

## Directory Structure
```
legal_dataset_pipeline/stage2_supreme_court/
│
├── supreme_court_judgments.json      # Structured dataset of 25 SC judgments
├── supreme_court_source_manifest.json  # Dataset provenance manifest
├── stage2_collection_report.md        # Comprehensive Stage 2 report
├── README.md                          # Pipeline documentation
└── scripts/
    └── validate_stage2.py             # 11-point automated validation engine
```

## Schema Format
Each record contains:
- `document_id`: Unique identifier (e.g. `SC_JUDGMENT_001`)
- `case_name`: Official case title
- `court`: `"Supreme Court of India"`
- `judgment_date`: `YYYY-MM-DD`
- `citation`: Official law report citation
- `relevant_bns_sections`: Array of mapped BNS section strings
- `legal_concepts`: Array of legal concepts / ratio decidendi
- `judgment_text`: Exact unmodified precedent excerpt
- `source_type`: `"Judicial_Precedent"`
- `authority`: `"Supreme Court of India"`
- `jurisdiction`: `"India"`
- `source_url`: Official legal portal URL
- `retrieval_date`: `YYYY-MM-DD`
- `verification_status`: `"VERIFIED"`

## Running Validation
To run the automated validation engine:
```bash
python legal_dataset_pipeline/stage2_supreme_court/scripts/validate_stage2.py
```
