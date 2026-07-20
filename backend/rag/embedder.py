"""문서·질문 임베딩.

실배포는 LiteLLM Proxy의 OpenAI 호환 /embeddings를 사용한다.
HashEmbedder는 API 키 없이 단위 테스트와 배관 확인에만 사용한다.
"""
from __future__ import annotations

import hashlib
import math
import re
import time
from typing import Protocol

import httpx

from . import config

_TOKEN = re.compile(r"[A-Za-z0-9_]+|[가-힣]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text or "")]


class Embedder(Protocol):
    name: str
    dim: int | None

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


def _l2(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


class HashEmbedder:
    def __init__(self, dim: int = 256):
        self.dim = dim
        self.name = f"hash:{dim}"

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in tokenize(text):
            bucket = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dim
            vector[bucket] += 1.0
        return _l2(vector)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._one(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._one(text)


class LiteLLMEmbedder:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.model = model or config.EMBED_MODEL
        self.base_url = (base_url or config.LITELLM_BASE_URL).rstrip("/")
        self.api_key = api_key or config.LITELLM_API_KEY
        self.name = f"litellm:{self.model}"
        self.dim: int | None = None

    def _request(self, inputs: list[str]) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": inputs}
        last_error: Exception | None = None
        for attempt in range(7):
            try:
                with httpx.Client(timeout=config.REQUEST_TIMEOUT) as client:
                    response = client.post(
                        f"{self.base_url}/embeddings",
                        headers=headers,
                        json=payload,
                    )
                response.raise_for_status()
                data = sorted(response.json()["data"], key=lambda item: item.get("index", 0))
                vectors = [[float(value) for value in item["embedding"]] for item in data]
                if len(vectors) != len(inputs):
                    raise RuntimeError(
                        f"임베딩 개수 불일치: input={len(inputs)}, output={len(vectors)}"
                    )
                dimensions = {len(vector) for vector in vectors}
                if len(dimensions) != 1:
                    raise RuntimeError(f"임베딩 차원이 일정하지 않습니다: {dimensions}")
                dimension = dimensions.pop()
                if self.dim is not None and self.dim != dimension:
                    raise RuntimeError(
                        f"임베딩 차원이 변경됐습니다: expected={self.dim}, actual={dimension}"
                    )
                self.dim = dimension
                return [_l2(vector) for vector in vectors]
            except (httpx.HTTPError, KeyError, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt == 6:
                    break
                time.sleep(min(5, 2**attempt))
        raise RuntimeError(f"LiteLLM 임베딩 호출 실패: {last_error}") from last_error

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), config.EMBED_BATCH_SIZE):
            vectors.extend(self._request(texts[start : start + config.EMBED_BATCH_SIZE]))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._request([text])[0]


def make_embedder(kind: str = "litellm", model: str | None = None) -> Embedder:
    if kind == "litellm":
        return LiteLLMEmbedder(model=model)
    if kind == "hash":
        return HashEmbedder()
    raise ValueError(f"알 수 없는 임베더: {kind}")
