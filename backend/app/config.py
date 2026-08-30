from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve Project Root reliably (config.py is at <PROJECT_ROOT>/backend/app/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
KB_ROOT_DIR = PROJECT_ROOT / "knowledge_base" / "trustgate_knowledge_base"


class Settings(BaseSettings):
    """
    Application Configuration Settings.
    Models and URLs are read from environment variables or default values.
    Do NOT hardcode models in business logic.
    """

    PROJECT_NAME: str = "TrustGate-AI"
    API_V1_STR: str = "/api/v1"

    # Ollama Local LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    CLAIM_EXTRACTION_MODEL: str = "qwen2.5:3b"
    VERIFICATION_MODEL: str = "gemma3:4b"

    # Environment Settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Knowledge Base & Retrieval Paths
    PROJECT_ROOT_PATH: Path = PROJECT_ROOT
    KB_ROOT_PATH: Path = KB_ROOT_DIR
    KB_CHUNKS_PATH: Path = KB_ROOT_DIR / "data" / "processed" / "BNS_2023_chunks.jsonl"
    KB_BM25_INDEX_PATH: Path = KB_ROOT_DIR / "indexes" / "bm25" / "bm25_index.json"
    KB_DENSE_EMBEDDINGS_PATH: Path = KB_ROOT_DIR / "indexes" / "dense" / "dense_embeddings.npy"
    KB_VECTORIZER_PATH: Path = KB_ROOT_DIR / "indexes" / "dense" / "vectorizer.joblib"
    KB_SVD_MODEL_PATH: Path = KB_ROOT_DIR / "indexes" / "dense" / "svd_model.joblib"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
