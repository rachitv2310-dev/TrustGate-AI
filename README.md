# TrustGate-AI

**TrustGate-AI** is a modular, claim-level verification system for detecting hallucinations and evaluating evidence grounding in AI-generated responses within the Indian legal domain.

---

## Architecture Overview

TrustGate-AI processes responses through a modular 5-step pipeline:

1. **Input Ingestion**: Accepts user legal prompt and AI response.
2. **Claim Extraction**: Decomposes paragraphs into atomic factual claims using configurable local LLMs (`qwen2.5:3b` / Ollama).
3. **Evidence Retrieval**: Queries legal knowledge bases for supporting/contradicting evidence passages.
4. **Claim-Evidence Verification**: Evaluates claim stance (`SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT`) using configurable verifier LLMs (`gemma3:4b` / Ollama).
5. **Trust Score Calculation**: Produces claim-level verdicts and an overall transparent trust report.

---

## Project Structure

```text
trustgate-ai/
│
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point & health check
│   │   ├── config.py             # Configurable settings (.env)
│   │   ├── api/routes/verify.py  # Verification API routes
│   │   ├── schemas/              # Pydantic schemas (Claim, Verification, Report)
│   │   ├── services/             # Core business logic services
│   │   ├── retrieval/            # Chunking, Embeddings & Vector Store interfaces
│   │   └── database/             # Database connection setup
│   ├── requirements.txt          # Minimum required dependencies
│   └── .env.example              # Environment variables template
│
├── knowledge_base/
│   ├── raw/                      # Raw legal texts
│   ├── processed/                # Chunked data & vector indexes
│   └── metadata/                 # Corpus metadata
│
├── frontend/                     # Web UI placeholder
├── docs/                         # Architecture documentation
└── README.md
```

---

## Current Development Status

- [x] Initial modular project folder structure & starter boilerplate
- [x] FastAPI application with `/health` endpoint
- [x] Configurable Ollama model settings (`config.py` / `.env`)
- [x] Pydantic schemas for Claim, Request, and Report models
- [ ] Atomic claim extraction service implementation (Phase 2)
- [ ] Legal knowledge base ingestion & hybrid retrieval pipeline (Phase 3)
- [ ] Claim verification & trust scoring engine (Phase 4)

---

## Installation & Quick Start

### 1. Requirements
- Python 3.10+
- Local [Ollama](https://ollama.com/) instance with models installed:
  ```bash
  ollama pull qwen2.5:3b
  ollama pull gemma3:4b
  ```

### 2. Setup Environment
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### 3. Run FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```

Verify health check endpoint:
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "ok",
  "service": "TrustGate-AI"
}
```
