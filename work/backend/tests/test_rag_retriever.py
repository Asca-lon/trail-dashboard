from __future__ import annotations

import pytest

from rag.embedder import HashEmbedder
from rag.repository import ChunkRecord, InMemoryRepository
from rag.retriever import _cosine, search


def _record(chunk_id: int, content: str, authority: str = "reference_document"):
    embedder = HashEmbedder()
    return ChunkRecord(
        chunk_id=chunk_id,
        path=f"doc{chunk_id}.md",
        section=f"s{chunk_id}",
        content=content,
        embedding=embedder.embed_query(content),
        authority=authority,
        source_type="markdown",
        language=None,
        git_commit="test",
        collection="project",
    )


def test_identifier_keyword_is_retrieved():
    repository = InMemoryRepository(
        records=[
            _record(1, "avg_delay_incr는 도착역 지연에서 출발역 지연을 뺀 값이다", "current_implementation"),
            _record(2, "지도 화면의 색상과 레이아웃을 설명한다"),
        ]
    )
    hits = search("avg_delay_incr 계산", HashEmbedder(), repository, top_k=1)
    assert hits[0].record.chunk_id == 1


def test_dimension_mismatch_raises():
    with pytest.raises(ValueError, match="차원 불일치"):
        _cosine([1.0, 0.0], [1.0])
