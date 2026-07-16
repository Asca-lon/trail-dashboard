"""
계약 동기화 테스트 — CONTRACT §5-1 을 코드로 강제한다.

  1) mock/*.json 이 models.py 와 항상 일치하는지 검증(누군가 한쪽만 고치면 빨간불).
  2) 응답 보장(정렬·필터검증·에러형식)이 실제로 지켜지는지 검증.
  3) 스코프 축소 회귀 방지 — 삭제하기로 한 것이 응답에 되살아나지 않는지.

실행:  cd backend && pytest -q   (DB 불필요, mock 모드)

── 이번 개정에서 바뀐 것 ─────────────────────────────────────
- 삭제: Case 모델 회귀 테스트          → cases[] 부재 테스트로 대체
- 삭제: /segment/{from}/{to} 검사      → 404(폐기) 검사 + /segments/details 추가
- 추가: 스코프 가드(강수량·예보·강풍·대설·사례)
- 추가: 식별자(station_id·segment_id·target_type) 존재 검사
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("USE_MOCK", "1")

from fastapi.testclient import TestClient  # noqa: E402

import api  # noqa: E402
import models  # noqa: E402

MOCK_DIR = Path(__file__).resolve().parent.parent.parent / "mock"
client = TestClient(api.app)

MOCK_MODEL_MAP = {
    "lines.json": models.LinesResponse,
    "vulnerability_segments.json": models.SegmentsResponse,
    "vulnerability_stations.json": models.StationsResponse,
    "heatmap.json": models.HeatmapResponse,
    "checklist.json": models.ChecklistResponse,
    "alerts_active.json": models.AlertsActiveResponse,
    "station_details.json": models.StationDetail,
    "segments_details.json": models.SegmentsDetailsResponse,
}

# 스코프 밖으로 확정된 필드 — 어느 응답에도 다시 나타나면 안 된다.
BANNED_KEYS = {
    "cases",             # 과거 사례 표: 화면에서 제거
    "rain_mm",           # 강수량: 특보 API 에 소스 없음
    "current_rain_mm",
    "affected_trains",   # cases 전용 필드였음
}
# 스코프 밖 특보 종류 (§1: 호우·폭염만)
BANNED_ALERT_TYPES = {"강풍", "대설", "태풍", "한파"}

ALL_ENDPOINTS = [
    "/health", "/lines", "/vulnerability/segments", "/vulnerability/stations",
    "/heatmap", "/checklist", "/alerts/active",
    "/station/daejeon", "/segments/details",
]


def _walk(node):
    """중첩 dict/list 를 전부 훑는다."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


# ── 1) mock ↔ models 동기화 ───────────────────────────────────
@pytest.mark.parametrize("filename,model", MOCK_MODEL_MAP.items())
def test_mock_matches_model(filename, model):
    path = MOCK_DIR / filename
    if not path.exists():
        pytest.skip(f"{filename} 아직 없음")
    model.model_validate(json.loads(path.read_text(encoding="utf-8")))


def test_every_mock_file_is_registered():
    on_disk = {p.name for p in MOCK_DIR.glob("*.json")}
    unregistered = on_disk - set(MOCK_MODEL_MAP)
    assert not unregistered, f"MOCK_MODEL_MAP 에 등록 필요: {unregistered}"


# ── 2) 응답 보장 (§5-1) ───────────────────────────────────────
def test_all_endpoints_ok():
    for path in ALL_ENDPOINTS:
        assert client.get(path).status_code == 200, path


def test_segments_sorted_desc():
    segs = client.get("/vulnerability/segments").json()["segments"]
    vals = [s["avg_delay_incr"] for s in segs]
    assert vals == sorted(vals, reverse=True)


def test_stations_sorted_desc():
    rows = client.get("/vulnerability/stations").json()["stations"]
    vals = [s["avg_delay"] for s in rows]
    assert vals == sorted(vals, reverse=True)


def test_segment_from_key_serialized():
    seg = client.get("/vulnerability/segments").json()["segments"][0]
    assert "from" in seg and "from_" not in seg


def test_segments_details_from_key_serialized():
    seg = client.get("/segments/details").json()["segments"][0]
    assert "from" in seg and "from_" not in seg


@pytest.mark.parametrize("bad", [
    {"alert_type": "없는특보"},
    {"alert_level": "없는레벨"},
    {"train_type": "없는열차"},
])
def test_invalid_filter_returns_contract_error(bad):
    r = client.get("/vulnerability/segments", params=bad)
    assert r.status_code == 400
    assert set(r.json()["error"]) == {"code", "message"}


@pytest.mark.parametrize("banned", sorted(BANNED_ALERT_TYPES))
def test_out_of_scope_alert_type_rejected(banned):
    r = client.get("/vulnerability/segments", params={"alert_type": banned})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_ALERT_TYPE"


def test_alerts_active_affected_shape():
    for alert in client.get("/alerts/active").json()["active"]:
        for aff in alert["affected"]:
            if aff["type"] == "station":
                assert "from" not in aff and "to" not in aff
            elif aff["type"] == "segment":
                assert "station" not in aff


# ── 3) 스코프 축소 회귀 방지 ──────────────────────────────────
@pytest.mark.parametrize("path", ALL_ENDPOINTS)
def test_no_banned_keys_in_response(path):
    """cases · 강수량 · affected_trains 가 어떤 응답에도 없어야 한다."""
    body = client.get(path).json()
    for node in _walk(body):
        leaked = BANNED_KEYS & set(node)
        assert not leaked, f"{path} 응답에 스코프 밖 필드: {leaked}"


@pytest.mark.parametrize("path", ALL_ENDPOINTS)
def test_no_out_of_scope_alert_types_in_response(path):
    """강풍 · 대설 등이 응답 어디에도 실려 나가면 안 된다."""
    body = client.get(path).json()
    for node in _walk(body):
        at = node.get("alert_type")
        assert at not in BANNED_ALERT_TYPES, f"{path} 응답에 스코프 밖 특보: {at}"


def test_hourly_delay_is_actual_only():
    """실적은 1일 지연 — 예보(forecast) 포인트는 만들지 않는다."""
    for seg in client.get("/segments/details").json()["segments"]:
        for point in seg["hourly_delay"]:
            assert point["type"] == "actual"


def test_forecast_point_rejected_by_model():
    with pytest.raises(Exception):
        models.SegmentHourlyDelay(time="20:00", delay_min=1.0, type="forecast")


def test_deprecated_segment_endpoint_is_gone():
    """구 /segment/{from}/{to} 는 /segments/details 로 대체됐다."""
    assert client.get("/segment/대전/김천(구미)").status_code == 404


def test_case_model_removed():
    assert not hasattr(models, "Case"), "Case 모델은 삭제됐다(과거 사례 제거)"
    assert not hasattr(models, "SegmentDetail"), "SegmentDetail → SegmentsDetailsResponse"


# ── 4) 식별자(C의 상세 페이지 링크) ──────────────────────────
def test_station_vuln_has_station_id():
    for s in client.get("/vulnerability/stations").json()["stations"]:
        assert s["station_id"] == models.station_slug(s["station"])


def test_station_vuln_delay_count_matches_estimate():
    """delay_count 는 round(sample_n * delay_rate) 와 일치해야 한다(프론트 추정식과 동일)."""
    for s in client.get("/vulnerability/stations").json()["stations"]:
        assert "delay_count" in s
        if s["delay_count"] is not None:
            assert s["delay_count"] == round(s["sample_n"] * s["delay_rate"])


def test_segment_vuln_has_segment_id():
    for s in client.get("/vulnerability/segments").json()["segments"]:
        assert s["segment_id"] == models.segment_slug(s["from"], s["to"])


def test_segments_details_has_segment_id():
    for s in client.get("/segments/details").json()["segments"]:
        assert s["segment_id"] == models.segment_slug(s["from"], s["to"])


def test_checklist_items_have_target_ids():
    for item in client.get("/checklist").json()["items"]:
        assert item["target_type"] in ("station", "segment")
        key = "station_id" if item["target_type"] == "station" else "segment_id"
        assert item.get(key), f"{item['target_type']} 항목에 {key} 없음"


def test_station_detail_accepts_slug_and_name():
    by_slug = client.get("/station/daejeon").json()
    by_name = client.get("/station/대전").json()
    assert by_slug["station"] == by_name["station"] == "대전"
    assert by_slug["station_id"] == by_name["station_id"] == "daejeon"


# ── 5) 역 상세 · 구간 상세의 새 필드 모양 ────────────────────
def test_station_detail_shape():
    d = client.get("/station/daejeon").json()
    assert set(d) == {"station_id", "station", "by_alert", "hourly_delay", "alert_delay_comparison"}
    # 시간대 차트: 4시간 버킷 7포인트, 마지막은 축을 닫는 24:00
    assert [p["time"] for p in d["hourly_delay"]] == [
        "00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"
    ]
    # 평시 vs 특보 비교는 호우·폭염 2행
    assert {c["alert_type"] for c in d["alert_delay_comparison"]} <= {"호우", "폭염"}


def test_segments_details_shape():
    seg = client.get("/segments/details").json()["segments"][0]
    assert set(seg) == {"segment_id", "from", "to", "hourly_delay", "delay_increase_trend", "by_alert"}
    assert [p["time"] for p in seg["hourly_delay"]] == [
        "00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"
    ]
    for b in seg["by_alert"]:
        # avg_delay 는 A가 컬럼 추가 전까지 null 가능. 키는 항상 존재(§5-1(2)).
        assert set(b) >= {"alert_type", "alert_level", "avg_delay",
                          "delay_increase", "stop_rate", "sample_n"}


def test_heatmap_without_alert_type_is_ok():
    """alert_type 생략 = 호우·폭염 전체. 한 종류로 고정하면 다른 종류만 겪은 역이
    '데이터 없음'으로 빠져 노선 전체를 보는 히트맵의 목적이 깨진다."""
    r = client.get("/heatmap")
    assert r.status_code == 200
    assert set(r.json()) == {"line", "nodes", "edges"}


def test_heatmap_node_per_station_is_unique():
    """역당 노드는 하나여야 한다.
    station_vulnerability 의 PK 가 (역, 종류, 등급)이라 조건 없이 JOIN 하면
    등급·종류별로 중복 노드가 생긴다(SQL 에서 MAX 로 합침)."""
    nodes = client.get("/heatmap").json()["nodes"]
    names = [n["station"] for n in nodes]
    assert len(names) == len(set(names)), f"중복 노드: {names}"
