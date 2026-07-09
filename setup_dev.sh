#!/usr/bin/env bash
# setup_dev.sh — 클론된 레포에 B의 변경분(테스트/설정)을 이식한다.
# 레포 루트(trail-dashboard/)에서 실행:  bash setup_dev.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo ">>> 레포 루트: $ROOT"

# ── 1) conftest.py (bare pytest 에서도 import 되게) ─────────────
cat > backend/conftest.py << 'EOF'
"""pytest 설정: backend/ 를 sys.path 에 넣어 `import api`, `import models` 가
어떤 실행 방식(pytest / python -m pytest)에서도 동작하게 한다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
EOF

# ── 2) 테스트 의존성 파일 ──────────────────────────────────────
cat > backend/requirements-dev.txt << 'EOF'
# 테스트 도구. 런타임에는 불필요.
#   pip install -r requirements-dev.txt  (requirements.txt 도 함께 설치됨)
-r requirements.txt
pytest
httpx          # fastapi TestClient 가 내부적으로 사용
EOF

# ── 3) 계약 동기화 테스트 ──────────────────────────────────────
mkdir -p backend/tests
cat > backend/tests/test_contract.py << 'EOF'
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
    # "station_detail.json": models.StationDetail,   # ← 상세 mock 작업에서 추가
    # "segment_detail.json": models.SegmentDetail,
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
EOF

# ── 4) models.py 패치: Case.alert_type -> Optional ─────────────
python3 - << 'PY'
from pathlib import Path
p = Path("backend/models.py"); s = p.read_text(encoding="utf-8")
old = "class Case(BaseModel):\n    date: str\n    alert_type: str\n"
new = ("class Case(BaseModel):\n    date: str\n"
       "    # nullable: 지연 사례의 특보 종류 매칭은 A(분석) 영역이라 null 일 수 있다.\n"
       "    alert_type: Optional[str] = None\n")
if old in s:
    p.write_text(s.replace(old, new), encoding="utf-8"); print("  models.py 패치 완료")
elif "alert_type: Optional[str] = None" in s:
    print("  models.py 이미 패치됨(건너뜀)")
else:
    raise SystemExit("  [경고] models.py 의 Case 블록을 못 찾음 — 수동 확인 필요")
PY

# ── 5) api.py 패치: load_dotenv 추가 ──────────────────────────
python3 - << 'PY'
from pathlib import Path
p = Path("backend/api.py"); s = p.read_text(encoding="utf-8")
anchor = "from fastapi.responses import JSONResponse\n\nfrom models import ("
inject = ("from fastapi.responses import JSONResponse\n\n"
          "from dotenv import load_dotenv\n"
          "load_dotenv(Path(__file__).resolve().parent.parent / \".env\")\n\n"
          "from models import (")
if "load_dotenv(" in s:
    print("  api.py 이미 패치됨(건너뜀)")
elif anchor in s:
    p.write_text(s.replace(anchor, inject), encoding="utf-8"); print("  api.py 패치 완료")
else:
    raise SystemExit("  [경고] api.py 의 import 지점을 못 찾음 — 수동 확인 필요")
PY

# ── 6) .env.example 채우기 ────────────────────────────────────
cat > .env.example << 'EOF'
# ── 앱 모드 ─────────────────────────────────────────────
# 1 = mock/*.json 응답 (A의 DB 없이도 동작하는 워킹 스켈레톤)
# 0 = 실제 DB 조회 (db.py, 읽기 전용)
USE_MOCK=1

# mock 디렉터리 (기본: backend 기준 ../mock)
# MOCK_DIR=../mock

# CORS 허용 오리진 (쉼표 구분). 개발은 *, 배포 전엔 좁힐 것.
CORS_ORIGINS=*

# ── 실제 DB (USE_MOCK=0 일 때만) ─────────────────────────
DATABASE_URL=postgresql://readonly:readonly@localhost:5432/trail
EOF

echo ">>> 파일 이식 완료."
echo ">>> 다음: 가상환경 활성화 후  pip install -r backend/requirements-dev.txt  &&  (cd backend && pytest)"
