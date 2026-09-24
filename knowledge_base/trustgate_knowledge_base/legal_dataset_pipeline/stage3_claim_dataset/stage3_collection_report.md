# Stage 3 — Legal Claim / Verification Dataset Collection Report

## 1. Objective
Construct a source-grounded, structured legal claim-verification testing dataset containing 120 records derived exclusively from the verified legal knowledge base established in Stage 1 (39 BNS Sections) and Stage 2 (25 Supreme Court Judgments).

## 2. Dataset Construction Methodology
- **Decomposition**: Realistic AI legal query-response pairs decomposed into atomic factual claims.
- **Evidence Linking**: Ground-truth mapping to verified Stage 1 (`BNS_SEC_*`) or Stage 2 (`SC_JUDGMENT_*`) documents.
- **Labeling Rules**:
  - `SUPPORTED`: Ground truth evidence explicitly confirms the claim.
  - `REFUTED`: Ground truth evidence explicitly contradicts the claim.
  - `INSUFFICIENT`: Ground truth evidence in Stage 1 / Stage 2 does not contain facts to prove/disprove the claim.

## 3. Dataset Metrics & Label Distribution
- **Total Records**: 120
- **Total Atomic Claims**: 120
- **BNS-Based Records**: 85 (70.8%)
- **Supreme Court-Based Records**: 35 (29.2%)
- **Label Distribution**:
  - `SUPPORTED`: 70 (58.3%)
  - `REFUTED`: 30 (25.0%)
  - `INSUFFICIENT`: 20 (16.7%)

## 4. Claim Type Distribution
- **LEGAL_PRINCIPLE**: 7 records
- **CASE_PRECEDENT**: 31 records
- **PUNISHMENT**: 15 records
- **SECTION_MAPPING**: 38 records
- **LEGAL_DEFINITION**: 4 records
- **STATUTORY_FACT**: 17 records
- **LEGAL_CONDITION**: 8 records


## 5. 14-Point Automated Quality & Validation Audit Results
1. **Record Count (100-150 Range)**: PASSED (120 records)
2. **Record ID Uniqueness**: PASSED (120 unique `record_id` values)
3. **Claim ID Uniqueness**: PASSED (120 unique `claim_id` values)
4. **Required Field Completeness**: PASSED (100% records contain all 13 mandatory fields)
5. **Valid Verification Labels**: PASSED (Only `SUPPORTED`, `REFUTED`, `INSUFFICIENT`)
6. **Evidence Document ID Validity**: PASSED (100% IDs exist in Stage 1 or Stage 2)
7. **BNS Evidence Mapping Validity**: PASSED (100% BNS claims mapped to `BNS_SEC_*`)
8. **Supreme Court Evidence Mapping Validity**: PASSED (100% SC claims mapped to `SC_JUDGMENT_*`)
9. **Empty Claim / Evidence Detection**: PASSED (Zero empty claims or text fields)
10. **Source Provenance Completeness**: PASSED (100% authority, URL, and basis populated)
11. **Duplicate Detection**: PASSED (Zero duplicate questions or claims)
12. **Stage 1 Preservation Check**: PASSED (Stage 1 files 100% untouched)
13. **Stage 2 Preservation Check**: PASSED (Stage 2 files 100% untouched)
14. **JSON Structural Validity**: PASSED (100% valid JSON syntax and schema compliance)

## 6. Sample Records Inventory (First 15 Records)

| Record ID | Claim Type | Verification Label | Evidence Doc ID | Question Excerpt | Claim Summary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `STAGE3_REC_001` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_001` | What is the core provision under BNS Sec... | BNS Section 1 governs Short title, commenceme... |
| `STAGE3_REC_002` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_002` | What is the core provision under BNS Sec... | BNS Section 2 governs Definitions.... |
| `STAGE3_REC_003` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_003` | What is the core provision under BNS Sec... | BNS Section 3 governs General explanations.... |
| `STAGE3_REC_004` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_004` | What is the core provision under BNS Sec... | BNS Section 4 governs Punishments.... |
| `STAGE3_REC_005` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_005` | What is the core provision under BNS Sec... | BNS Section 5 governs Commutation  of  senten... |
| `STAGE3_REC_006` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_006` | What is the core provision under BNS Sec... | BNS Section 6 governs Fractions  of  terms  o... |
| `STAGE3_REC_007` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_007` | What is the core provision under BNS Sec... | BNS Section 7 governs Sentence may be (in cer... |
| `STAGE3_REC_008` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_008` | What is the core provision under BNS Sec... | BNS Section 8 governs Amount of fine, liabili... |
| `STAGE3_REC_009` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_014` | What is the core provision under BNS Sec... | BNS Section 14 governs Act  done  by  a  pers... |
| `STAGE3_REC_010` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_018` | What is the core provision under BNS Sec... | BNS Section 18 governs Accident in doing a la... |
| `STAGE3_REC_011` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_020` | What is the core provision under BNS Sec... | BNS Section 20 governs Act of a child under s... |
| `STAGE3_REC_012` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_022` | What is the core provision under BNS Sec... | BNS Section 22 governs Act of a person of uns... |
| `STAGE3_REC_013` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_034` | What is the core provision under BNS Sec... | BNS Section 34 governs Things done in private... |
| `STAGE3_REC_014` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_035` | What is the core provision under BNS Sec... | BNS Section 35 governs Right of private defen... |
| `STAGE3_REC_015` | `SECTION_MAPPING` | `SUPPORTED` | `BNS_SEC_038` | What is the core provision under BNS Sec... | BNS Section 38 governs When  right  of  priva... |


## 7. Limitations & Stage 4 Readiness
- **Dataset Role**: This dataset serves as a benchmark testing corpus for claim extraction, evidence retrieval, and verification pipelines.
- **Stage 4 Readiness**: The pipeline is fully prepared for **Stage 4** execution.
- **Final Readiness Status**: `READY_FOR_STAGE_4`
