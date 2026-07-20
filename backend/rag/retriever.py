"""벡터 + 키워드 + 문서 권위 가중치를 합친 하이브리드 검색."""
from __future__ import annotations

import math
from dataclasses import dataclass

from . import config
from .embedder import Embedder, tokenize
from .repository import ChunkRecord, InMemoryRepository


@dataclass
class Hit:
    record: ChunkRecord
    score: float
    vector_score: float
    keyword_score: float


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError(
            f"임베딩 차원 불일치: query={len(left)}, document={len(right)}. "
            "같은 임베딩 모델로 다시 인제스트하세요."
        )
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    value = sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)
    return max(0.0, min(1.0, value))


def _is_identifier(token: str) -> bool:
    return "_" in token or (
        any(character.isalpha() for character in token)
        and any(character.isdigit() for character in token)
    )


def _keyword_score(query_tokens: list[str], content: str) -> float:
    if not query_tokens:
        return 0.0
    content_tokens = set(tokenize(content))
    hit = 0.0
    total = 0.0
    for token in query_tokens:
        weight = 2.0 if _is_identifier(token) else 1.0
        total += weight
        if token in content_tokens:
            hit += weight
    return hit / total if total else 0.0


def search(
    query: str,
    embedder: Embedder,
    repository: InMemoryRepository,
    collection: str | None = None,
    top_k: int | None = None,
) -> list[Hit]:
    collection = collection or config.COLLECTION
    top_k = top_k or config.TOP_K
    query_vector = embedder.embed_query(query)
    query_tokens = tokenize(query)

    hits: list[Hit] = []
    for record in repository.all(collection):
        vector_score = _cosine(query_vector, record.embedding)
        keyword_score = _keyword_score(query_tokens, record.content)
        base = config.W_VEC * vector_score + config.W_KW * keyword_score
        authority = config.AUTHORITY_WEIGHT.get(record.authority, 0.70)
        hits.append(
            Hit(
                record=record,
                score=base * authority,
                vector_score=vector_score,
                keyword_score=keyword_score,
            )
        )

    hits.sort(key=lambda hit: hit.score, reverse=True)

    # 같은 파일·섹션·페이지의 유사 청크가 결과를 독점하지 않도록 중복 제거한다.
    seen: set[tuple[str, str | None, int | None]] = set()
    result: list[Hit] = []
    for hit in hits:
        key = (hit.record.path, hit.record.section, hit.record.page_number)
        if key in seen:
            continue
        seen.add(key)
        result.append(hit)
        if len(result) >= top_k:
            break
    return result
