"""RAG 런타임 설정.

LiteLLM Proxy를 단일 모델 게이트웨이로 사용한다. 실제 공급자 모델은
litellm/config.yaml과 .env에서 바꾸고, 애플리케이션은 alias만 사용한다.
"""
from __future__ import annotations

import os
from pathlib import Path

COLLECTION = os.getenv("RAG_COLLECTION", "project")
ENABLED = os.getenv("RAG_ENABLED", "0") == "1"
INDEX_FILE = Path(os.getenv("RAG_INDEX_FILE", "/data/rag_index.json"))

# LiteLLM OpenAI-compatible proxy
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://litellm:4000/v1").rstrip("/")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", os.getenv("LITELLM_MASTER_KEY", "sk-local-dev"))
CHAT_MODEL = os.getenv("RAG_CHAT_MODEL", "rag-chat")
EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "rag-embedding")
EMBED_PROVIDER_MODEL = os.getenv("RAG_EMBED_PROVIDER_MODEL", "unknown")
REQUEST_TIMEOUT = float(os.getenv("RAG_REQUEST_TIMEOUT", "90"))
EMBED_BATCH_SIZE = int(os.getenv("RAG_EMBED_BATCH_SIZE", "32"))

# 검색
TOP_K = int(os.getenv("RAG_TOP_K", "5"))
CANDIDATE_K = int(os.getenv("RAG_CANDIDATE_K", "20"))
W_VEC = float(os.getenv("RAG_W_VEC", "0.7"))
W_KW = float(os.getenv("RAG_W_KW", "0.3"))
MAX_CONTEXT_CHARS = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "9000"))
AUTHORITY_WEIGHT = {
    "current_implementation": 1.00,
    "approved_document": 0.92,
    "reference_document": 0.78,
}

# 청킹
CHUNK_MAX_CHARS = int(os.getenv("RAG_CHUNK_MAX", "1200"))
CHUNK_OVERLAP_CHARS = int(os.getenv("RAG_CHUNK_OVERLAP", "160"))
CHUNK_MIN_CHARS = int(os.getenv("RAG_CHUNK_MIN", "50"))

_SRC_BY_EXT = {
    ".py": "source_code",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".jsx": "javascript",
    ".md": "markdown",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".txt": "text",
    ".pdf": "pdf",
}
_LANG_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
}


def authority_for(path: str) -> str:
    """최신 실행 코드가 과거 설계 문서보다 우선하도록 권위 등급을 지정한다."""
    p = path.replace("\\", "/").lstrip("./")
    if (
        p.startswith(("backend/", "processor/", "collector/", "db/"))
        or p.endswith(".sql")
    ):
        return "current_implementation"
    if p in {"CONTRACT.md", "README.md", "RAG_Ask_Contract.md"}:
        return "approved_document"
    return "reference_document"


def source_type_for(path: str) -> str:
    return _SRC_BY_EXT.get(Path(path).suffix.lower(), "text")


def language_for(path: str) -> str | None:
    return _LANG_BY_EXT.get(Path(path).suffix.lower())
