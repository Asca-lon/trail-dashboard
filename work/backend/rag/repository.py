"""파일 기반 RAG 인덱스 저장소.

MVP는 서버의 Docker volume에 JSON 인덱스를 저장한다. API는 파일 수정 시각이
바뀌면 자동으로 다시 읽으므로 인제스트 후 API를 재시작할 필요가 없다.
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ChunkRecord:
    chunk_id: int
    path: str
    section: str | None
    content: str
    embedding: list[float]
    authority: str
    source_type: str
    language: str | None
    git_commit: str
    collection: str
    page_number: int | None = None


class InMemoryRepository:
    def __init__(self, records: list[ChunkRecord] | None = None, meta: dict | None = None):
        self.records = records or []
        self.meta = meta or {}

    def all(self, collection: str) -> list[ChunkRecord]:
        return [record for record in self.records if record.collection == collection]

    def save(self, path: Path, meta: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"meta": meta, "records": [asdict(record) for record in self.records]}
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(path)

    @classmethod
    def load(cls, path: Path) -> "InMemoryRepository":
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
        return cls(
            records=[ChunkRecord(**record) for record in payload.get("records", [])],
            meta=payload.get("meta", {}),
        )


class IndexCache:
    """인덱스 파일을 프로세스 메모리에 캐시하고 mtime 변경 시 다시 읽는다."""

    def __init__(self, path: Path):
        self.path = path
        self._mtime_ns: int | None = None
        self._repository: InMemoryRepository | None = None
        self._lock = threading.Lock()

    def get(self) -> InMemoryRepository:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        mtime_ns = self.path.stat().st_mtime_ns
        if self._repository is not None and self._mtime_ns == mtime_ns:
            return self._repository
        with self._lock:
            mtime_ns = self.path.stat().st_mtime_ns
            if self._repository is None or self._mtime_ns != mtime_ns:
                self._repository = InMemoryRepository.load(self.path)
                self._mtime_ns = mtime_ns
        return self._repository
