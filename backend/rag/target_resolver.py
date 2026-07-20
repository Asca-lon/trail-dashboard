"""자유 질문과 화면 context에서 역·구간 조회 대상을 규칙으로 결정한다."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from models import SLUG_TO_STATION, STATION_SLUGS, segment_slug, station_slug

LINE_ORDER: list[str] = [
    "서울",
    "광명",
    "천안아산",
    "오송",
    "대전",
    "김천구미",
    "동대구",
    "경주",
    "울산",
    "부산",
]

STATION_ALIASES: dict[str, str] = {
    "서울": "서울",
    "광명": "광명",
    "천안아산": "천안아산",
    "천안": "천안아산",
    "아산": "천안아산",
    "오송": "오송",
    "대전": "대전",
    "김천구미": "김천구미",
    "김천(구미)": "김천구미",
    "김천": "김천구미",
    "구미": "김천구미",
    "동대구": "동대구",
    "대구": "동대구",
    "경주": "경주",
    "울산": "울산",
    "부산": "부산",
}

_STRONG_SEGMENT = ("구간", "사이")
_WEAK_SEGMENT = ("~", "→", "-")
_COMPARISON = ("비교", "vs", "보다", "어디가", " 중 ", "중에", "중 어")

_unknown = {name for name in STATION_ALIASES.values() if name not in STATION_SLUGS}
if _unknown:
    raise RuntimeError(f"STATION_SLUGS에 없는 정식 역명: {_unknown}")
if set(LINE_ORDER) != set(STATION_SLUGS):
    raise RuntimeError("LINE_ORDER와 STATION_SLUGS의 역 집합이 다릅니다")

Kind = Literal["station", "segment", "stations", "none"]
ResolutionMethod = Literal["context", "text_match", "none"]


@dataclass
class Target:
    target_type: Literal["station", "segment"]
    target_id: str
    name: str


@dataclass
class Resolution:
    kind: Kind
    targets: list[Target]
    resolution: ResolutionMethod
    note: str | None = None


def resolve(question: str, context: dict | None = None, max_stations: int = 3) -> Resolution:
    if context:
        context_result = _from_context(context)
        if context_result is not None:
            return context_result
    return _from_text(question or "", max_stations=max_stations)


def _from_context(context: dict) -> Resolution | None:
    target_type = context.get("target_type")
    target_id = context.get("target_id")
    if not isinstance(target_id, str) or not target_id:
        return None

    if target_type == "station":
        if target_id in SLUG_TO_STATION:
            name = SLUG_TO_STATION[target_id]
        elif target_id in STATION_SLUGS:
            name = target_id
        else:
            return None
        return Resolution(
            kind="station",
            targets=[Target("station", station_slug(name), name)],
            resolution="context",
        )

    if target_type == "segment":
        pair = _split_segment_id(target_id)
        if pair is None:
            return None
        return Resolution(
            kind="segment",
            targets=[_segment_target(*pair)],
            resolution="context",
        )
    return None


def _split_segment_id(segment_id: str) -> tuple[str, str] | None:
    parts = segment_id.split("-")
    if len(parts) != 2:
        return None
    from_name = SLUG_TO_STATION.get(parts[0])
    to_name = SLUG_TO_STATION.get(parts[1])
    if from_name is None or to_name is None or not _adjacent(from_name, to_name):
        return None
    return from_name, to_name


def _from_text(question: str, max_stations: int) -> Resolution:
    names = _extract_stations(question)
    if not names:
        return Resolution("none", [], "none")
    if len(names) == 1:
        name = names[0]
        return Resolution(
            "station",
            [Target("station", station_slug(name), name)],
            "text_match",
        )

    if _segment_intent(question):
        pair = _first_adjacent_pair(names)
        if pair is not None:
            note = None
            if len(names) > 2:
                note = "여러 역이 언급되어 인접한 두 역을 구간으로 해석했습니다."
            return Resolution(
                "segment",
                [_segment_target(*pair)],
                "text_match",
                note=note,
            )
        targets = [
            Target("station", station_slug(name), name)
            for name in names[:max_stations]
        ]
        return Resolution(
            "stations",
            targets,
            "text_match",
            note=(
                "언급된 역들이 노선상 인접하지 않아 단일 구간이 아닙니다. "
                "각 역 기준으로 설명합니다."
            ),
        )

    targets = [
        Target("station", station_slug(name), name)
        for name in names[:max_stations]
    ]
    return Resolution("stations", targets, "text_match")


def _extract_stations(text: str) -> list[str]:
    consumed = [False] * len(text)
    hits: list[tuple[int, str]] = []
    for alias in sorted(STATION_ALIASES, key=len, reverse=True):
        start = 0
        while True:
            index = text.find(alias, start)
            if index < 0:
                break
            span = range(index, index + len(alias))
            if not any(consumed[position] for position in span):
                for position in span:
                    consumed[position] = True
                hits.append((index, STATION_ALIASES[alias]))
            start = index + 1

    hits.sort(key=lambda item: item[0])
    result: list[str] = []
    seen: set[str] = set()
    for _, name in hits:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _segment_intent(text: str) -> bool:
    if any(marker in text for marker in _STRONG_SEGMENT):
        return True
    comparison = any(marker in text for marker in _COMPARISON)
    weak = (
        any(marker in text for marker in _WEAK_SEGMENT)
        or ("에서" in text and "까지" in text)
        or "가는" in text
    )
    return weak and not comparison


def _adjacent(left: str, right: str) -> bool:
    return abs(LINE_ORDER.index(left) - LINE_ORDER.index(right)) == 1


def _first_adjacent_pair(names: list[str]) -> tuple[str, str] | None:
    for left_index in range(len(names)):
        for right_index in range(left_index + 1, len(names)):
            if _adjacent(names[left_index], names[right_index]):
                return names[left_index], names[right_index]
    return None


def _segment_target(left: str, right: str) -> Target:
    if LINE_ORDER.index(left) > LINE_ORDER.index(right):
        left, right = right, left
    return Target("segment", segment_slug(left, right), f"{left}–{right}")
