import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "AI Support Agent"
    ENV: str = os.getenv("ENV", "dev")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RAW_DOCS_DIR: str = os.path.join(DATA_DIR, "raw_docs")
    FAISS_INDEX_DIR: str = os.path.join(DATA_DIR, "faiss_index")

    # Embeddings (HF)
    HF_EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Retrieval settings
    TOP_K_RETRIEVER: int = 20   # initial FAISS candidates
    TOP_K_RERANK: int = 5       # final chunks sent to LLM

    # RAG / business rules
    TOP_K: int = 5
    ESCALATION_CONFIDENCE_THRESHOLD: float = 0.55


settings = Settings()
