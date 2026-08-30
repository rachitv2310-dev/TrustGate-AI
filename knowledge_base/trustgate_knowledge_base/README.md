# TrustGate-AI Legal Knowledge Base & Claim–Evidence Dataset

## 1. Primary Purpose & Scope Definition
This repository (`trustgate_knowledge_base`) is constructed **exclusively** as a trusted legal dataset / knowledge-base construction and evaluation repository built around the Bharatiya Nyaya Sanhita, 2023.

> **"This dataset is constructed for future use by the TrustGate-AI project. This repository does not contain the final TrustGate-AI application."**

### What This Repository Is:
- A trusted legal evidence collection, ingestion, parsing, chunking, and validation pipeline.
- A structured, provenance-preserved **Claim–Evidence Dataset** (`data/dataset/`) containing 60 verified claim-evidence examples across 7 legal claim categories with section-aware splits.
- A research and evaluation benchmark environment for legal document retrieval (BM25, LSA Dense, and Hybrid Score Fusion).
- An evidence-quality and claim-evidence verification research evaluation pipeline.

### What This Repository Is NOT:
- **NOT** the final user-facing TrustGate-AI application, product, web UI, or chatbot.
- **NOT** a production REST API, Flask/FastAPI web server, or user authentication system.
- **NOT** an autonomous legal advice system or legal truth generator.
- The main TrustGate application logic, frontend, and production deployment reside in separate repositories.

---

## 2. Pipeline & Dataset Construction Architecture

```
Official Primary Legal Source (India Code Gazette PDF)
        ↓ [CHUNK 3: Provenance & SHA-256 Verification]
Raw Immutable PDF (data/raw/Bharatiya_Nyaya_Sanhita_2023.pdf)
        ↓ [CHUNK 4: Text Extraction & Quality Validation]
Extracted Legal Text (data/processed/BNS_2023_text.txt)
        ↓ [CHUNK 5: Hierarchy & Structure Parsing]
Structured Legal Hierarchy (20 Chapters, 358 Sections)
        ↓ [CHUNK 6: Legal-Aware Chunk Generation]
392 Retrieval Chunks (data/processed/BNS_2023_chunks.jsonl)
        ↓ [CHUNK 7: Dataset Validation & Integrity Checks]
Validated Dataset (100% Offset & Provenance Match)
        │
        ├─────────────────────────┬─────────────────────────┐
        ▼                         ▼                         ▼
[CHUNK 8–10: Retrieval]   [CHUNK 11: Reranking]   [CHUNK 15: Claim–Evidence Dataset]
  BM25, Dense, Hybrid       Multi-Feature Linear    60 Supervised Examples (data/dataset/)
  Searchability Evaluation  Candidate Ordering      7 Claim Types | Section-Aware Splits
        └─────────────────────────┴─────────────────────────┘
                                  │
                                  ▼
                     [CHUNK 12–14: Research Evaluation]
                       Claim–Evidence Verification, Trust Score (Evidence Quality),
                       and Research Report Generation (data/reports/)
```

---

## 3. Directory Structure & Dataset Artifacts

- **`config/`**: System governance policies, trusted source registry (`trusted_sources.json`), source authority tiers (`source_authority.json`), and validation schemas. *(Core Dataset Component)*
- **`data/`**: Root folder for legal document data.
  - **`data/raw/`**: Storage for raw legal source documents. **Raw legal documents are immutable and must NEVER be modified.** *(Core Dataset Component)*
  - **`data/processed/`**: Extracted text, structured legal hierarchy, prepared chunk datasets (`BNS_2023_chunks.jsonl`), dataset reports, and evaluation results. *(Core Dataset Component)*
  - **`data/dataset/`**: **Constructed Claim–Evidence Supervised & Evaluation Dataset** *(CHUNK 15 Deliverable)*:
    - `claim_evidence_dataset.jsonl` (60 complete records)
    - `train.jsonl` (34 records - section-aware split)
    - `validation.jsonl` (12 records - section-aware split)
    - `test.jsonl` (14 records - section-aware split)
    - `hard_negatives.jsonl` (14 hard negative records)
    - `out_of_domain.jsonl` (4 out-of-domain negative control records)
    - `dataset_schema.json` (JSON Schema definition)
  - **`data/reports/`**: Generated explainable JSON and Markdown research verification reports for benchmark claims (`CLAIM_001` to `CLAIM_012`). *(Research Evaluation Component)*
  - **`data/validated/`**: Designated folder for validated release datasets. *(Core Dataset Component)*
- **`indexes/`**: Storage for generated search and retrieval indexes.
  - **`indexes/bm25/`**: Serialized BM25 term frequency matrices and metadata. *(Retrieval Research Component)*
  - **`indexes/dense/`**: Serialized 128-dimensional LSA dense vector embeddings (`dense_embeddings.npy`) and projection models. *(Retrieval Research Component)*
- **`scripts/`**: Python modules for dataset extraction, parsing, chunking, claim-evidence dataset construction (`build_claim_evidence_dataset.py`), validation (`validate_claim_evidence_dataset.py`), and evaluation experiments. *(Dataset & Research Component)*

---

## 4. Claim–Evidence Dataset Schema & Categories

The dataset includes 60 verified examples across 7 legal claim categories:
1. `DIRECT_SUPPORTED` (18 records): Claims directly supported by BNS legal provisions.
2. `DIRECT_REFUTED` (10 records): Claims directly contradicted by BNS legal provisions.
3. `SECTION_MISMATCH` (8 hard negatives): Correct legal definition assigned to wrong section number.
4. `CROSS_SECTION_CONFUSION` (6 hard negatives): Confuses legal provisions across multiple sections.
5. `PARTIALLY_SUPPORTED` (6 records): Part of proposition supported, remaining unestablished.
6. `INSUFFICIENT_EVIDENCE` (8 records): Related legal topic mentioned, but specific proposition not established.
7. `OUT_OF_DOMAIN` (4 negative controls): Non-legal topics (e.g. quantum computing, tax law) with zero false evidence.

**Data Leakage Prevention**: Split into `train` (34), `validation` (12), and `test` (14) using section-aware partitioning to prevent claims from the same legal section from appearing in both train and test splits.

---

## 5. Architectural Disclaimer & Terminology

- **Legal Knowledge Base**: A structured, verified, and traceable collection of official legal source texts.
- **Evidence Quality / Trust Score**: A 0.0 to 100.0 research evaluation metric measuring evidence relevance, sufficiency, source authority, and consistency.
- **Disclaimer**: *The verification and trust-score components are research/evaluation artifacts and do not independently establish legal truth or provide legal advice.*
