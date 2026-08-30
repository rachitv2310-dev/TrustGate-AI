# TrustGate-AI Architecture Documentation

## Overview

**TrustGate-AI** is a claim-level verification system designed to detect hallucinations and evaluate factual groundings in AI-generated responses within the Indian legal domain.

---

## High-Level Verification Workflow

```text
Input (VerificationRequest)
        ↓
Claim Extraction (ClaimExtractorService)
        ↓
Retrieval (EvidenceRetrieverService)
        ↓
Verification (ClaimVerifierService → VerificationVerdict)
        ↓
Trust Score (TrustScoreCalculatorService)
        ↓
Final Report (VerificationReport)
```

---

## Module Responsibilities

### 1. `backend/app/main.py`
- Initializes the FastAPI web application instance.
- Defines core health check (`GET /health`) and registers router endpoints under `/api/v1`.

### 2. `backend/app/config.py`
- Manages application configuration via Pydantic `BaseSettings` reading from `.env`.
- Stores configurable settings like `OLLAMA_BASE_URL`, `CLAIM_EXTRACTION_MODEL`, and `VERIFICATION_MODEL` so LLM choices are never hardcoded.

### 3. `backend/app/api/`
- **`routes/verify.py`**: Defines verification API endpoint contracts (`POST /api/v1/verify`).

### 4. `backend/app/schemas/`
- **`claim.py`**: Pydantic data model for `Claim` (`id`, `text`, `type`, `importance`, `verifiable`, `verdict`, `evidence`) and `VerificationVerdict` (`SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT`).
- **`verification.py`**: Data schemas for incoming verification requests (`VerificationRequest`).
- **`report.py`**: Data schema for final structured verification reports (`VerificationReport`).

### 5. `backend/app/services/`
- **`pipeline.py`**: Orchestrator service placeholder (`VerificationPipeline`) for the end-to-end workflow.
- **`llm_service.py`**: Interacts with local Ollama instance over HTTP API using models specified in config.
- **`claim_extractor.py`**: Parses raw LLM text into atomic, testable claims.
- **`retriever.py`**: Interfaces with retrieval engines to fetch legal evidence for claims.
- **`verifier.py`**: Evaluates `(Claim, Evidence)` pairs to produce `VerificationVerdict`.
- **`trust_score.py`**: Calculates overall trust score (placeholder for future logic).

### 6. `backend/app/retrieval/`
- **`chunker.py`**: Document chunking utilities optimized for legal text structures.
- **`embeddings.py`**: Embedding generation service wrapper.
- **`vector_store.py`**: Vector store search interface placeholder.

### 7. `backend/app/database/`
- **`connection.py`**: Database session dependency provider placeholder.

### 8. `knowledge_base/`
- Stores legal corpus files separated into `raw/` (unprocessed legal texts), `processed/` (chunked & indexed data), and `metadata/`.

### 9. `frontend/`
- Reserved directory for future web UI.
