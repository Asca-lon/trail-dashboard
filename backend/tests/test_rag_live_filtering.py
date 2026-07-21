from __future__ import annotations

import api

from rag.router import (
    RagContext,
    _collect_live_targets,
)
from rag.target_resolver import Resolution, Target


def test_station_metrics_use_screen_filters(monkeypatch):
    captured = {}

    def fake_get_stations(
        line="경부선",
        alert_type=None,
        alert_level=None,
    ):
        captured.update(
            {
                "line": line,
                "alert_type": alert_type,
                "alert_level": alert_level,
            }
        )

        return {
            "stations": [
                {
                    "station_id": "daejeon",
                    "station": "대전",
                    "avg_delay": 4.2,
                    "delta_delay": 2.1,
                    "delay_rate": 0.31,
                    "stop_rate": 0.0,
                    "sample_n": 85,
                    "delay_count": 26,
                    "risk_level": "warning",
                    "confidence": "normal",
                    "risk_reason": "테스트 근거",
                }
            ]
        }

    monkeypatch.setattr(
        api,
        "get_stations",
        fake_get_stations,
    )

    context = RagContext.model_validate(
        {
            "page_type": "station_detail",
            "target_type": "station",
            "target_id": "daejeon",
            "filters": {
                "line": "경부선",
                "alert_type": "호우",
                "alert_level": "경보",
            },
        }
    )

    resolution = Resolution(
        kind="station",
        targets=[
            Target(
                target_type="station",
                target_id="daejeon",
                name="대전",
            )
        ],
        resolution="context",
    )

    targets = _collect_live_targets(
        resolution,
        context,
    )

    assert captured == {
        "line": "경부선",
        "alert_type": "호우",
        "alert_level": "경보",
    }

    assert len(targets) == 1
    assert targets[0].target_id == "daejeon"
    assert targets[0].metrics["sample_n"] == 85


def test_segment_metrics_use_screen_filters(monkeypatch):
    captured = {}

    def fake_get_segments(
        line="경부선",
        alert_type=None,
        alert_level=None,
        train_type=None,
    ):
        captured.update(
            {
                "line": line,
                "alert_type": alert_type,
                "alert_level": alert_level,
                "train_type": train_type,
            }
        )

        return {
            "segments": [
                {
                    "segment_id":
                        "daejeon-gimcheon_gumi",
                    "from": "대전",
                    "to": "김천구미",
                    "avg_delay_incr": 3.4,
                    "stop_rate": 0.02,
                    "sample_n": 120,
                    "risk_level": "warning",
                    "confidence": "normal",
                    "risk_reason": "테스트 근거",
                }
            ]
        }

    monkeypatch.setattr(
        api,
        "get_segments",
        fake_get_segments,
    )

    context = RagContext.model_validate(
        {
            "page_type": "route_detail",
            "target_type": "segment",
            "target_id":
                "daejeon-gimcheon_gumi",
            "filters": {
                "line": "경부선",
                "alert_type": "폭염",
                "alert_level": "주의보",
                "train_type": "KTX",
            },
        }
    )

    resolution = Resolution(
        kind="segment",
        targets=[
            Target(
                target_type="segment",
                target_id:
                    "daejeon-gimcheon_gumi",
                name="대전–김천구미",
            )
        ],
        resolution="context",
    )

    targets = _collect_live_targets(
        resolution,
        context,
    )

    assert captured == {
        "line": "경부선",
        "alert_type": "폭염",
        "alert_level": "주의보",
        "train_type": "KTX",
    }

    assert len(targets) == 1
    assert (
        targets[0].target_id
        == "daejeon-gimcheon_gumi"
    )


def test_all_filter_values_are_omitted(monkeypatch):
    captured = {}

    def fake_get_stations(
        line="경부선",
        alert_type=None,
        alert_level=None,
    ):
        captured.update(
            {
                "line": line,
                "alert_type": alert_type,
                "alert_level": alert_level,
            }
        )
        return {"stations": []}

    monkeypatch.setattr(
        api,
        "get_stations",
        fake_get_stations,
    )

    context = RagContext.model_validate(
        {
            "page_type": "dashboard",
            "filters": {
                "line": "경부선",
                "alert_type": "all",
                "alert_level": "전체",
                "train_type": "all",
            },
        }
    )

    resolution = Resolution(
        kind="station",
        targets=[
            Target(
                target_type="station",
                target_id="daejeon",
                name="대전",
            )
        ],
        resolution="text_match",
    )

    _collect_live_targets(
        resolution,
        context,
    )

    assert captured == {
        "line": "경부선",
        "alert_type": None,
        "alert_level": None,
    }
