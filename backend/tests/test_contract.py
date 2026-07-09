"""
계약 동기화 테스트 — CONTRACT_V5 §5-1 을 코드로 강제한다.

  1) mock/*.json 이 models.py 와 항상 일치하는지 검증(누군가 한쪽만 고치면 빨간불).
  2) 응답 보장(정렬·필터검증·에러형식)이 실제로 지켜지는지 검증.
  3) Case.alert_type nullable 회귀 방지.

실행:  cd backend && pytest -q   (DB 불필요, mock 모드)
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
    "station_detail.json": models.StationDetail,
    "segment_detail.json": models.SegmentDetail,
}


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


def test_all_endpoints_ok():
    for path in [
        "/health", "/lines", "/vulnerability/segments", "/vulnerability/stations",
        "/heatmap", "/checklist", "/alerts/active",
        "/station/대전", "/segment/대전/김천(구미)",
    ]:
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


@pytest.mark.parametrize("bad", [
    {"alert_type": "없는특보"},
    {"alert_level": "없는레벨"},
    {"train_type": "없는열차"},
])
def test_invalid_filter_returns_contract_error(bad):
    r = client.get("/vulnerability/segments", params=bad)
    assert r.status_code == 400
    assert set(r.json()["error"]) == {"code", "message"}


def test_alerts_active_affected_shape():
    for alert in client.get("/alerts/active").json()["active"]:
        for aff in alert["affected"]:
            if aff["type"] == "station":
                assert "from" not in aff and "to" not in aff
            elif aff["type"] == "segment":
                assert "station" not in aff


def test_case_alert_type_nullable():
    models.Case(date="2026-07-01", alert_type=None, delay_min=5)
