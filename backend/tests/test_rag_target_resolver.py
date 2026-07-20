from __future__ import annotations

import pytest

from rag.target_resolver import resolve


@pytest.mark.parametrize(
    "question,target_id",
    [
        ("대전역은 왜 주의로 분류됐어?", "daejeon"),
        ("김천 지연 어때?", "gimcheon_gumi"),
        ("대구역 취약도", "dongdaegu"),
    ],
)
def test_station_aliases(question: str, target_id: str):
    result = resolve(question)
    assert result.kind == "station"
    assert result.targets[0].target_id == target_id


@pytest.mark.parametrize(
    "question",
    [
        "대전에서 김천 구간 취약도",
        "대전~김천 어때",
        "김천에서 대전 가는 구간",
    ],
)
def test_segment_direction_is_normalized(question: str):
    result = resolve(question)
    assert result.kind == "segment"
    assert result.targets[0].target_id == "daejeon-gimcheon_gumi"


def test_comparison_is_not_segment():
    result = resolve("대전이랑 오송 중 어디가 더 취약해?")
    assert result.kind == "stations"
    assert {target.target_id for target in result.targets} == {"daejeon", "osong"}


def test_non_adjacent_segment_falls_back_to_stations():
    result = resolve("서울에서 부산 구간이 궁금해")
    assert result.kind == "stations"
    assert result.note is not None


def test_no_target_uses_none_resolution():
    result = resolve("event_time은 어떤 시각이야?")
    assert result.kind == "none"
    assert result.resolution == "none"
    assert result.targets == []


def test_context_overrides_question():
    result = resolve(
        "대전은 왜 이래?",
        context={"target_type": "station", "target_id": "osong"},
    )
    assert result.resolution == "context"
    assert result.targets[0].target_id == "osong"


def test_invalid_context_falls_back_to_text():
    result = resolve(
        "부산역은 어때?",
        context={"target_type": "station", "target_id": "unknown"},
    )
    assert result.resolution == "text_match"
    assert result.targets[0].target_id == "busan"
