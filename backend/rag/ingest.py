"""프로젝트 문서와 소스 코드를 청킹·임베딩해 파일 인덱스로 저장한다.

컨테이너 실행 예:
    cd /app/backend
    python -m rag.ingest --repo /app --embedder litellm
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .chunker import load_and_chunk
from .embedder import make_embedder
from .repository import ChunkRecord, InMemoryRepository

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".sql",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".html",
    ".css",
    ".txt",
    ".pdf",
}
EXCLUDE_PARTS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    ".pytest_cache",
    "assets",
    "data",
    "logs",
    "results",
    "uploads",
    "tests",
}
EXCLUDE_NAMES = {"conftest.py"}


def _git_commit(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _iter_files(repo: Path):
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        relative = path.relative_to(repo)
        if any(part in EXCLUDE_PARTS for part in relative.parts):
            continue
        if path.name in EXCLUDE_NAMES:
            continue
        yield relative, path


def _read_text(path: Path) -> str | None:
    if path.suffix.lower() == ".pdf":
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def ingest(repo: Path, embedder_kind: str, output: Path) -> dict:
    commit = _git_commit(repo)
    embedder = make_embedder(embedder_kind)
    records: list[ChunkRecord] = []
    document_count = 0
    next_id = 1
    started_at = datetime.now(timezone.utc).isoformat()

    for relative, absolute in _iter_files(repo):
        path = str(relative).replace("\\", "/")
        text = _read_text(absolute)
        chunks = load_and_chunk(path, text=text, absolute_path=absolute)
        if not chunks:
            continue
        vectors = embedder.embed_documents([chunk.content for chunk in chunks])
        if len(vectors) != len(chunks):
            raise RuntimeError(f"청크와 임베딩 수가 다릅니다: {path}")
        for chunk, vector in zip(chunks, vectors):
            records.append(
                ChunkRecord(
                    chunk_id=next_id,
                    path=path,
                    section=chunk.section,
                    content=chunk.content,
                    embedding=vector,
                    authority=config.authority_for(path),
                    source_type=config.source_type_for(path),
                    language=config.language_for(path),
                    git_commit=commit,
                    collection=config.COLLECTION,
                    page_number=chunk.page_number,
                )
            )
            next_id += 1
        document_count += 1
        print(
            f"  {path:55} {len(chunks):3d} chunks "
            f"[{config.authority_for(path)}]"
        )

    if not records:
        raise RuntimeError("인제스트 대상 문서가 없습니다")

    # 동일 인덱스인지 확인할 수 있는 가벼운 콘텐츠 지문.
    digest = hashlib.sha256()
    for record in records:
        digest.update(record.path.encode("utf-8"))
        digest.update(record.content.encode("utf-8"))

    meta = {
        "collection": config.COLLECTION,
        "git_commit": commit,
        "embedder": embedder.name,
        "embedding_provider_model": config.EMBED_PROVIDER_MODEL,
        "embedding_dim": len(records[0].embedding),
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "document_count": document_count,
        "chunk_count": len(records),
        "content_sha256": digest.hexdigest(),
    }
    InMemoryRepository(records=records, meta=meta).save(output, meta)
    print(
        f"완료 — 문서 {document_count}, 청크 {len(records)}, "
        f"commit {commit}, {embedder.name}, {output}"
    )
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="..", help="프로젝트 루트")
    parser.add_argument(
        "--embedder", choices=["litellm", "hash"], default="litellm"
    )
    parser.add_argument("--output", default=str(config.INDEX_FILE))
    args = parser.parse_args()
    ingest(
        repo=Path(args.repo).resolve(),
        embedder_kind=args.embedder,
        output=Path(args.output),
    )


if __name__ == "__main__":
    main()
