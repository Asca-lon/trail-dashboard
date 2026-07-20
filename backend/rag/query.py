"""RAG 검색 결과를 LLM 호출 없이 터미널에서 확인한다."""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from . import config
from .embedder import make_embedder
from .repository import InMemoryRepository
from .retriever import search
from .target_resolver import resolve


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=config.TOP_K)
    parser.add_argument("--index", default=str(config.INDEX_FILE))
    args = parser.parse_args()

    repository = InMemoryRepository.load(Path(args.index))
    descriptor = str(repository.meta.get("embedder", ""))
    if descriptor.startswith("litellm:"):
        embedder = make_embedder("litellm", model=descriptor.split(":", 1)[1])
    elif descriptor.startswith("hash:"):
        embedder = make_embedder("hash")
    else:
        raise RuntimeError(f"알 수 없는 인덱스 임베더: {descriptor}")

    resolution = resolve(args.question)
    target_text = ", ".join(
        f"{target.target_type}:{target.target_id}" for target in resolution.targets
    ) or "-"
    print(f"질문: {args.question}")
    print(
        f"대상: kind={resolution.kind}, resolution={resolution.resolution}, "
        f"targets=[{target_text}]"
    )
    print(
        f"인덱스: commit={repository.meta.get('git_commit')}, "
        f"embedder={descriptor}, chunks={repository.meta.get('chunk_count')}\n"
    )

    for index, hit in enumerate(
        search(args.question, embedder, repository, top_k=args.k), start=1
    ):
        record = hit.record
        section = f" > {record.section}" if record.section else ""
        print(
            f"[{index}] score={hit.score:.3f} "
            f"(vec={hit.vector_score:.2f}, kw={hit.keyword_score:.2f}) "
            f"[{record.authority}]"
        )
        print(f"    {record.path}{section}")
        snippet = " ".join(record.content.split())[:220]
        print(textwrap.indent(textwrap.fill(snippet, 92), "    ") + "\n")


if __name__ == "__main__":
    main()
