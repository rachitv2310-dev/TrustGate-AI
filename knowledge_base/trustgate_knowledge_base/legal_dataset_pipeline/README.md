# Legal Dataset and Knowledge Base Construction Pipeline

A source-grounded, quality-controlled legal dataset construction and validation pipeline for Indian statutory laws.

---

## 1. Purpose of this Pipeline
The primary objective of this pipeline is to extract, structure, and validate legal statutory data from official government legal sources (such as India Code and the Official Gazette of India) into standardized section-level JSON records.

This pipeline enforces strict source-first principles:
- **Zero Fabrication**: Statutory text, titles, numbers, and metadata are never invented, guessed, or paraphrased.
- **Full Provenance**: Every section record is traceable back to its official URL, enacting authority, jurisdiction, and retrieval date.
- **Quality Assurance**: Integrated 10-point quality control engine ensures zero missing fields, zero duplicates, and strict schema compliance.
- **Repository Isolation**: Operates independently from downstream AI, retrieval, or application modules.

---

## 2. Folder Structure

```
legal_dataset_pipeline/
│
├── data/
│   ├── raw/                 # Unaltered official source documents & digital extraction JSONs
│   ├── processed/           # Intermediate structured extraction files
│   ├── knowledge_base/      # Formatted section-level Knowledge Base JSON datasets
│   └── validation/          # Automated validation report JSON outputs
│
├── schemas/
│   └── knowledge_base_schema.json  # Formal JSON Schema specification (Draft-07 compliant)
│
├── scripts/
│   ├── build_pilot_kb.py           # Pipeline script transforming raw source data into KB records
│   └── validate_knowledge_base.py   # 10-point automated quality validation suite
│
├── reports/
│   └── pilot_validation_report.md  # Comprehensive execution and validation report
│
└── README.md                # This operational guide and pipeline documentation
```

---

## 3. Knowledge Base Record Format

Each legal section record is stored as an independent JSON object formatted as follows:

```json
{
  "document_id": "BNS_2023_SEC_103",
  "act_name": "Bharatiya Nyaya Sanhita, 2023",
  "act_number": "Act No. 45 of 2023",
  "section_number": "103",
  "section_title": "Punishment for murder",
  "chapter": "Chapter VI",
  "chapter_title": "Of Offences Affecting the Human Body",
  "text": "(1) Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.\n(2) When a group of five or more persons acting in concert commits murder on the ground of race, caste or community, sex, place of birth, language, personal belief or any other similar ground each member of such group shall be punished with death or with imprisonment for life, and shall also be liable to fine.",
  "source_type": "Primary_Law",
  "authority": "Parliament of India",
  "jurisdiction": "India",
  "effective_date": "2024-07-01",
  "source_url": "https://www.indiacode.nic.in/show-data?actid=AC_CEN_5_23_00045_202345_1717505307392&sectionId=103",
  "retrieval_date": "2026-08-27",
  "source_status": "VERIFIED",
  "notes": "Verified statutory text extracted from official India Code digital repository."
}
```

---

## 4. Verification Status Definitions

Every record MUST have an explicit `source_status` tag:

| Status Value | Meaning | Guidelines |
| :--- | :--- | :--- |
| `VERIFIED` | **Fully Verified Official Legal Data** | Text, title, number, and metadata have been directly verified against official government legal sources (e.g. India Code or Gazette of India). |
| `UNVERIFIED` | **Third-Party / Unconfirmed Data** | Information obtained from non-official sources or pending manual verification. Requires explicit reasoning in `notes`. |
| `PENDING_OFFICIAL_VERIFICATION` | **Sample / Placeholder Record** | Synthetic or placeholder data used during pipeline development. Must NEVER be passed as verified legal data. |

---

## 5. How Validation Works

The validation script `scripts/validate_knowledge_base.py` runs a 10-point inspection suite:

1. **JSON Validity**: Validates basic JSON syntax and structure.
2. **Required Field Completeness**: Ensures all 16 mandatory fields are present and non-empty.
3. **Duplicate Document IDs**: Detects conflicting `document_id` keys.
4. **Duplicate Section Records**: Detects duplicate `(act_name, section_number)` entries.
5. **Empty Legal Text**: Rejects records with missing, empty, or whitespace-only statutory text.
6. **Missing Source URL**: Verifies valid `http://` or `https://` official source URL format.
7. **Missing Retrieval Date**: Enforces ISO `YYYY-MM-DD` date formatting.
8. **Invalid Source Status**: Enforces valid enum values (`VERIFIED`, `UNVERIFIED`, `PENDING_OFFICIAL_VERIFICATION`).
9. **Missing Provenance**: Ensures `authority`, `jurisdiction`, and `source_type` are populated.
10. **Placeholder Check**: Flag any record marked `VERIFIED` that contains placeholder keywords (e.g., `[PLACEHOLDER]`, `lorem ipsum`, `TODO`).

---

## 6. How to Run the Scripts

### Generate / Build the Knowledge Base Dataset
To construct the structured JSON Knowledge Base from raw official source data:
```bash
python legal_dataset_pipeline/scripts/build_pilot_kb.py
```

### Run Knowledge Base Validation
To run the 10-point quality control engine:
```bash
python legal_dataset_pipeline/scripts/validate_knowledge_base.py
```

### Run Formal JSON Schema Check
To run standard schema validation via Python `jsonschema`:
```bash
python -c "import json, jsonschema; schema=json.load(open('legal_dataset_pipeline/schemas/knowledge_base_schema.json')); data=json.load(open('legal_dataset_pipeline/data/knowledge_base/bns_2023_pilot_kb.json')); jsonschema.validate(data, schema); print('JSON Schema validation PASSED!')"
```

---

## 7. How to Add a New Act or Additional Sections

### Step 1: Store Raw Official Data
1. Fetch official statutory text from India Code (`https://www.indiacode.nic.in`).
2. Create a new raw source file in `legal_dataset_pipeline/data/raw/<ACT_IDENTIFIER>_raw.json`.
3. Include official metadata (`act_name`, `act_number`, `authority`, `enforcement_date`, `retrieval_date`, `official_url`) and individual raw sections.

### Step 2: Transform to Knowledge Base Record
1. Ensure each section record receives a unique `document_id` (format: `<ACT_ID>_SEC_<SECTION_NUMBER>`).
2. Preserve exact official statutory text without paraphrasing or modification.
3. Assign appropriate `source_status` (`VERIFIED` only if directly verified against India Code).

### Step 3: Run Validation & Review Report
1. Execute `python legal_dataset_pipeline/scripts/validate_knowledge_base.py`.
2. Inspect `data/validation/validation_report.json` and ensure `FAILED RECORDS: 0`.
