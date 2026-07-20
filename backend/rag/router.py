"""POST /rag/ask — 프로젝트 문서 검색 + 라이브 취약도 지표 + LiteLLM 설명."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from . import config
from .embedder import make_embedder
from .litellm_client import LiteLLMClientError, chat
from .repository import IndexCache
from .retriever import Hit, search
from .target_resolver import Resolution, Target, resolve

router = APIRouter(prefix="/rag", tags=["RAG"])
_index_cache = IndexCache(config.INDEX_FILE)


class RagContext(BaseModel):
    target_type: Literal["station", "segment"]
    target_id: str


class RagAskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    collection: str = "project"
    context: RagContext | None = None


class RagSource(BaseModel):
    path: str
    section: str | None = None
    page_number: int | None = None
    score: float


class RagTarget(BaseModel):
    target_type: Literal["station", "segment"]
    target_id: str
    name: str
    metrics: dict[str, Any]
    risk_level: str | None = None
    confidence: str | None = None
    risk_reason: str | None = None


class RagAskResponse(BaseModel):
    answer: str
    targets: list[RagTarget]
    resolution: Literal["context", "text_match", "none"]
    sources: list[RagSource]
    limitations: list[str]


class RagHealthResponse(BaseModel):
    enabled: bool
    index_ready: bool
    index_file: str
    collection: str
    chat_model: str
    embedding_model: str
    document_count: int = 0
    chunk_count: int = 0
    git_commit: str | None = None


def _app_error(status: int, code: str, message: str) -> Exception:
    # serve.py가 api import를 끝낸 뒤 이 router를 등록하므로 요청 시점에는 안전하다.
    from api import AppError

    return AppError(status, code, message)


def _load_repository():
    try:
        repository = _index_cache.get()
    except FileNotFoundError as exc:
        raise _app_error(
            503,
            "RAG_INDEX_NOT_READY",
            "RAG 인덱스가 없습니다. rag-ingest를 먼저 실행하세요.",
        ) from exc
    if repository.meta.get("collection") != config.COLLECTION:
        raise _app_error(500, "RAG_INDEX_INVALID", "RAG 컬렉션이 설정과 다릅니다")
    return repository


def _embedder_for_index(meta: dict):
    descriptor = str(meta.get("embedder", ""))
    if descriptor.startswith("litellm:"):
        indexed_model = descriptor.split(":", 1)[1]
        if indexed_model != config.EMBED_MODEL:
            raise _app_error(
                503,
                "RAG_MODEL_MISMATCH",
                (
                    f"인덱스 임베딩 alias({indexed_model})와 현재 설정"
                    f"({config.EMBED_MODEL})이 다릅니다. 다시 인제스트하세요."
                ),
            )
        indexed_provider = str(meta.get("embedding_provider_model", "unknown"))
        if (
            indexed_provider != "unknown"
            and config.EMBED_PROVIDER_MODEL != "unknown"
            and indexed_provider != config.EMBED_PROVIDER_MODEL
        ):
            raise _app_error(
                503,
                "RAG_MODEL_MISMATCH",
                (
                    f"인덱스 공급자 임베딩 모델({indexed_provider})과 현재 설정"
                    f"({config.EMBED_PROVIDER_MODEL})이 다릅니다. 다시 인제스트하세요."
                ),
            )
        return make_embedder("litellm", model=indexed_model)
    if descriptor.startswith("hash:"):
        return make_embedder("hash")
    raise _app_error(500, "RAG_INDEX_INVALID", "알 수 없는 인덱스 임베더입니다")


def _station_metrics(targets: list[Target]) -> list[RagTarget]:
    from api import get_stations

    payload = get_stations(line="경부선")
    rows = {row.get("station_id"): row for row in payload.get("stations", [])}
    result: list[RagTarget] = []
    for target in targets:
        row = rows.get(target.target_id)
        if not row:
            continue
        metrics = {
            key: row.get(key)
            for key in (
                "avg_delay",
                "delta_delay",
                "delay_rate",
                "stop_rate",
                "sample_n",
                "delay_count",
            )
        }
        result.append(
            RagTarget(
                target_type="station",
                target_id=target.target_id,
                name=target.name,
                metrics=metrics,
                risk_level=row.get("risk_level"),
                confidence=row.get("confidence"),
                risk_reason=row.get("risk_reason"),
            )
        )
    return result


def _segment_metrics(target: Target) -> list[RagTarget]:
    from api import get_segments

    payload = get_segments(line="경부선")
    row = next(
        (
            item
            for item in payload.get("segments", [])
            if item.get("segment_id") == target.target_id
        ),
        None,
    )
    if not row:
        return []
    metrics = {
        key: row.get(key)
        for key in ("avg_delay_incr", "stop_rate", "sample_n")
    }
    return [
        RagTarget(
            target_type="segment",
            target_id=target.target_id,
            name=target.name,
            metrics=metrics,
            risk_level=row.get("risk_level"),
            confidence=row.get("confidence"),
            risk_reason=row.get("risk_reason"),
        )
    ]


def _collect_live_targets(resolution: Resolution) -> list[RagTarget]:
    if resolution.kind in {"station", "stations"}:
        return _station_metrics(resolution.targets)
    if resolution.kind == "segment" and resolution.targets:
        return _segment_metrics(resolution.targets[0])
    return []


def _source_payload(hits: list[Hit]) -> list[RagSource]:
    return [
        RagSource(
            path=hit.record.path,
            section=hit.record.section,
            page_number=hit.record.page_number,
            score=round(hit.score, 4),
        )
        for hit in hits
    ]


def _context_block(hits: list[Hit]) -> str:
    blocks: list[str] = []
    used = 0
    for index, hit in enumerate(hits, start=1):
        location = hit.record.path
        if hit.record.section:
            location += f" > {hit.record.section}"
        if hit.record.page_number:
            location += f" (p.{hit.record.page_number})"
        block = f"[SOURCE {index}] {location}\n{hit.record.content.strip()}"
        remaining = config.MAX_CONTEXT_CHARS - used
        if remaining <= 0:
            break
        if len(block) > remaining:
            block = block[:remaining]
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks)


def _limitations(resolution: Resolution, targets: list[RagTarget]) -> list[str]:
    result = [
        "답변은 프로젝트 문서·소스 코드와 대시보드가 제공한 지표만 사용합니다.",
        "사고·차량고장·실시간 운행 통제 원인은 추론하지 않습니다.",
    ]
    if resolution.note:
        result.append(resolution.note)
    if any(target.confidence == "insufficient" for target in targets):
        result.append("표본이 부족한 대상은 위험 등급을 단정할 수 없습니다.")
    return result


def _build_prompts(
    question: str,
    targets: list[RagTarget],
    hits: list[Hit],
    resolution: Resolution,
) -> tuple[str, str]:
    system_prompt = """당신은 철도 기상 취약구간 대시보드의 프로젝트 지식 도우미다.
반드시 제공된 프로젝트 근거와 라이브 지표만 사용해 한국어로 답한다.
수치와 risk_reason은 그대로 설명하고 재계산하거나 새로운 원인을 추론하지 않는다.
현재 구현과 과거 설계가 다르면 현재 구현을 우선하고 차이를 밝힌다.
confidence가 insufficient이면 등급을 단정하지 않는다.
근거가 없으면 확인할 수 없다고 말한다.
답변은 2~5문단으로 작성하고 출처 파일 경로를 마지막에 간단히 언급한다."""
    user_prompt = (
        f"질문:\n{question}\n\n"
        f"대상 해석:\n{json.dumps({'kind': resolution.kind, 'note': resolution.note}, ensure_ascii=False)}\n\n"
        f"라이브 지표:\n{json.dumps([target.model_dump() for target in targets], ensure_ascii=False, indent=2)}\n\n"
        f"검색 근거:\n{_context_block(hits)}"
    )
    return system_prompt, user_prompt


@router.get("/health", response_model=RagHealthResponse)
def rag_health() -> RagHealthResponse:
    meta: dict = {}
    ready = config.INDEX_FILE.exists()
    if ready:
        try:
            meta = _index_cache.get().meta
        except Exception:
            ready = False
    return RagHealthResponse(
        enabled=config.ENABLED,
        index_ready=ready,
        index_file=str(config.INDEX_FILE),
        collection=config.COLLECTION,
        chat_model=config.CHAT_MODEL,
        embedding_model=config.EMBED_MODEL,
        document_count=int(meta.get("document_count", 0)),
        chunk_count=int(meta.get("chunk_count", 0)),
        git_commit=meta.get("git_commit"),
    )


@router.post("/ask", response_model=RagAskResponse)
def rag_ask(request: RagAskRequest) -> RagAskResponse:
    if not config.ENABLED:
        raise _app_error(503, "RAG_DISABLED", "RAG_ENABLED=1로 설정해야 합니다")
    if request.collection != config.COLLECTION:
        raise _app_error(400, "INVALID_COLLECTION", "현재 collection은 project만 지원합니다")

    repository = _load_repository()
    embedder = _embedder_for_index(repository.meta)
    context = request.context.model_dump() if request.context else None
    resolution = resolve(request.question, context=context)

    try:
        hits = search(
            query=request.question,
            embedder=embedder,
            repository=repository,
            collection=request.collection,
            top_k=config.TOP_K,
        )
    except Exception as exc:
        raise _app_error(502, "RAG_RETRIEVAL_FAILED", str(exc)) from exc

    targets = _collect_live_targets(resolution)
    if not hits and not targets:
        return RagAskResponse(
            answer="프로젝트 문서와 현재 지표에서 질문의 근거를 확인할 수 없습니다.",
            targets=[],
            resolution=resolution.resolution,
            sources=[],
            limitations=_limitations(resolution, targets),
        )

    system_prompt, user_prompt = _build_prompts(
        request.question, targets, hits, resolution
    )
    try:
        answer = chat(system_prompt, user_prompt)
    except LiteLLMClientError as exc:
        raise _app_error(502, "LITELLM_ERROR", str(exc)) from exc

    return RagAskResponse(
        answer=answer,
        targets=targets,
        resolution=resolution.resolution,
        sources=_source_payload(hits),
        limitations=_limitations(resolution, targets),
    )
