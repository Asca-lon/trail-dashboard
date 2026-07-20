"""파일 유형별 텍스트 추출과 구조 보존 청킹."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import config


@dataclass
class Chunk:
    content: str
    section: str | None
    chunk_index: int
    page_number: int | None = None


def _window(text: str, max_chars: int, overlap: int) -> list[str]:
    """너무 긴 단일 블록도 반드시 max_chars 이하로 자른다."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    step = max(1, max_chars - overlap)
    return [text[i : i + max_chars].strip() for i in range(0, len(text), step) if text[i : i + max_chars].strip()]


def _pack_paragraphs(text: str) -> list[str]:
    out: list[str] = []
    buf = ""
    for para in re.split(r"\n\s*\n", text.strip()):
        para = para.strip()
        if not para:
            continue
        if len(para) > config.CHUNK_MAX_CHARS:
            if buf:
                out.append(buf)
                buf = ""
            out.extend(_window(para, config.CHUNK_MAX_CHARS, config.CHUNK_OVERLAP_CHARS))
            continue
        candidate = f"{buf}\n\n{para}" if buf else para
        if len(candidate) > config.CHUNK_MAX_CHARS:
            out.append(buf)
            buf = para
        else:
            buf = candidate
    if buf:
        out.append(buf)
    return out


def _chunk_markdown(text: str) -> list[tuple[str, str | None, int | None]]:
    sections: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s+", line):
            if body:
                sections.append((current_heading, "\n".join(body).strip()))
            current_heading = re.sub(r"^#{1,6}\s+", "", line).strip()
            body = [line]
        else:
            body.append(line)
    if body:
        sections.append((current_heading, "\n".join(body).strip()))

    out: list[tuple[str, str | None, int | None]] = []
    for heading, section_text in sections:
        for piece in _pack_paragraphs(section_text):
            out.append((piece, heading, None))
    return out


def _python_blocks(text: str) -> list[tuple[str, str | None, int | None]]:
    """top-level def/class와 바로 앞 decorator를 한 블록으로 유지한다."""
    lines = text.splitlines(keepends=True)
    starts: list[int] = []
    for i, line in enumerate(lines):
        if re.match(r"^(?:async\s+def|def|class)\s+", line):
            start = i
            while start > 0 and re.match(r"^@", lines[start - 1]):
                start -= 1
            starts.append(start)
    starts = sorted(set(starts))
    if not starts:
        return [(p, None, None) for p in _pack_paragraphs(text)]
    if starts[0] != 0:
        starts.insert(0, 0)

    out: list[tuple[str, str | None, int | None]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        block = "".join(lines[start:end]).strip()
        if not block:
            continue
        match = re.search(r"(?:async\s+def|def|class)\s+([A-Za-z0-9_]+)", block)
        section = match.group(1) if match else None
        for piece in _pack_paragraphs(block):
            out.append((piece, section, None))
    return out


def _javascript_blocks(text: str) -> list[tuple[str, str | None, int | None]]:
    pattern = r"^(?:export\s+)?(?:async\s+)?(?:function\s+|class\s+|const\s+|let\s+)"
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if re.match(pattern, line)]
    if not starts:
        return [(p, None, None) for p in _pack_paragraphs(text)]
    if starts[0] != 0:
        starts.insert(0, 0)
    out: list[tuple[str, str | None, int | None]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        block = "".join(lines[start:end]).strip()
        match = re.search(r"(?:function|class|const|let)\s+([A-Za-z0-9_]+)", block)
        section = match.group(1) if match else None
        for piece in _pack_paragraphs(block):
            out.append((piece, section, None))
    return out


def _sql_blocks(text: str) -> list[tuple[str, str | None, int | None]]:
    out: list[tuple[str, str | None, int | None]] = []
    for statement in re.split(r";\s*(?:\n|$)", text):
        statement = statement.strip()
        if not statement:
            continue
        match = re.search(
            r"CREATE\s+(?:TABLE|EXTENSION|INDEX)\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z0-9_.\"]+)",
            statement,
            re.IGNORECASE,
        )
        section = match.group(1).strip('"') if match else None
        for piece in _pack_paragraphs(statement + ";"):
            out.append((piece, section, None))
    return out


def _pdf_chunks(path: Path) -> list[tuple[str, str | None, int | None]]:
    from pypdf import PdfReader

    out: list[tuple[str, str | None, int | None]] = []
    reader = PdfReader(str(path))
    for page_index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        for piece in _pack_paragraphs(text):
            out.append((piece, f"page {page_index}", page_index))
    return out


def load_and_chunk(path: str, text: str | None = None, absolute_path: Path | None = None) -> list[Chunk]:
    source_type = config.source_type_for(path)
    if source_type == "pdf":
        if absolute_path is None:
            raise ValueError("PDF 청킹에는 absolute_path가 필요합니다")
        triples = _pdf_chunks(absolute_path)
    else:
        text = text or ""
        if source_type == "markdown":
            triples = _chunk_markdown(text)
        elif source_type == "source_code":
            triples = _python_blocks(text)
        elif source_type == "javascript":
            triples = _javascript_blocks(text)
        elif source_type == "sql":
            triples = _sql_blocks(text)
        elif source_type == "json":
            triples = [(p, Path(path).name, None) for p in _pack_paragraphs(text)]
        else:
            triples = [(p, None, None) for p in _pack_paragraphs(text)]

    chunks: list[Chunk] = []
    for index, (content, section, page_number) in enumerate(triples):
        if len(content.strip()) < config.CHUNK_MIN_CHARS:
            continue
        chunks.append(
            Chunk(
                content=content.strip(),
                section=section,
                chunk_index=index,
                page_number=page_number,
            )
        )
    return chunks
