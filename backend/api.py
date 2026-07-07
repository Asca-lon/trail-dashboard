"""
api.py — B(백엔드) FastAPI. CONTRACT_V5 §5 를 그대로 노출한다.

두 가지 모드:
  USE_MOCK=1 (기본)  → mock/*.json 을 응답. A의 DB 없이도 오늘 바로 돌아가는 워킹 스켈레톤.
  USE_MOCK=0          → db.py 로 A가 채운 집계 테이블을 읽어 응답(읽기 전용).

두 모드 모두 **같은 계약 모양**으로 응답하므로, C 입장에선 URL도 안 바꾸고 넘어간다.
전환은 B가 환경변수 하나만 바꾸면 끝(§7 "URL만 교체"의 백엔드판).

응답 보장(§5-1): 키 항상 존재 / 빈 값은 [] · null / 순위는 취약도 내림차순 / 숫자는 숫자 /
지연=분, 비율=0~1 / 빈 데이터는 200+[], 오류만 4xx·5xx + {"error":{code,message}}.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    LinesResponse, SegmentsResponse, StationsResponse, HeatmapResponse,
    StationDetail, SegmentDetail, ChecklistResponse, AlertsActiveResponse,
)

# ── 설정 ──────────────────────────────────────────────────────
USE_MOCK = os.getenv("USE_MOCK", "1") == "1"
MOCK_DIR = Path(os.getenv("MOCK_DIR", Path(__file__).resolve().parent.parent / "mock"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
KST = timezone(timedelta(hours=9))

# 필터 허용값 (§5-1 (4)) — C가 자유 입력하지 않도록 B가 방어.
ALERT_TYPES = {"대설", "호우", "폭염", "강풍", "태풍", "한파"}
ALERT_LEVELS = {"주의보", "경보"}
TRAIN_TYPES = {"all", "KTX", "무궁화", "새마을"}

app = FastAPI(title="경부선 기상 취약구간 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS, allow_methods=["GET"], allow_headers=["*"],
)


# ── 공통 에러 (§5-1 (3)) : 항상 {"error":{code,message}} ───────
class AppError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message

def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})

@app.exception_handler(AppError)
async def _app_error(_: Request, e: AppError):
    return _err(e.status, e.code, e.message)

@app.exception_handler(Exception)
async def _unhandled(_: Request, e: Exception):
    # 내부 오류도 계약 모양으로. (상세는 로그로, 응답엔 노출 안 함)
    return _err(500, "INTERNAL_ERROR", "서버 내부 오류")


def _check(alert_type=None, alert_level=None, train_type=None):
    if alert_type is not None and alert_type not in ALERT_TYPES:
        raise AppError(400, "INVALID_ALERT_TYPE", f"허용되지 않은 alert_type: {alert_type}")
    if alert_level is not None and alert_level not in ALERT_LEVELS:
        raise AppError(400, "INVALID_ALERT_LEVEL", f"허용되지 않은 alert_level: {alert_level}")
    if train_type is not None and train_type not in TRAIN_TYPES:
        raise AppError(400, "INVALID_TRAIN_TYPE", f"허용되지 않은 train_type: {train_type}")


def _mock(name: str) -> dict:
    with open(MOCK_DIR / name, encoding="utf-8") as f:
        return json.load(f)


@app.get("/health")
def health():
    return {"status": "ok", "mode": "mock" if USE_MOCK else "db"}


# ── GET /lines ────────────────────────────────────────────────
@app.get("/lines", response_model=LinesResponse)
def get_lines():
    if USE_MOCK:
        return _mock("lines.json")
    from db import fetch_all
    rows = fetch_all(
        "SELECT line, station_name, seq_on_line "
        "FROM stations ORDER BY line, seq_on_line NULLS LAST"
    )
    lines: dict[str, list[str]] = {}
    for r in rows:
        lines.setdefault(r["line"], []).append(r["station_name"])
    return {"lines": [{"line": k, "stations": v} for k, v in lines.items()]}


# ── GET /vulnerability/segments ───────────────────────────────
@app.get("/vulnerability/segments", response_model=SegmentsResponse)
def get_segments(line: str = "경부선", alert_type: str = "호우",
                 alert_level: str = "경보", train_type: str = "all"):
    _check(alert_type, alert_level, train_type)
    if USE_MOCK:
        d = _mock("vulnerability_segments.json")
        d["line"], d["alert_type"], d["alert_level"] = line, alert_type, alert_level
        return d
    from db import fetch_all
    # NOTE(계약 갭): 현재 segment_vulnerability(§4)에는 train_type 컬럼이 없다.
    # train_type 필터는 A가 집계에 차원을 추가해야 실제 동작한다. 지금은 무시(all 취급).
    rows = fetch_all(
        'SELECT from_station AS "from", to_station AS "to", '
        "avg_delay_incr, stop_rate, sample_n "
        "FROM segment_vulnerability "
        "WHERE line=%(line)s AND alert_type=%(at)s AND alert_level=%(al)s "
        "ORDER BY avg_delay_incr DESC NULLS LAST",
        {"line": line, "at": alert_type, "al": alert_level},
    )
    return {"line": line, "alert_type": alert_type, "alert_level": alert_level, "segments": rows}


# ── GET /vulnerability/stations ───────────────────────────────
@app.get("/vulnerability/stations", response_model=StationsResponse)
def get_stations(line: str = "경부선", alert_type: str = "폭염", alert_level: str = "경보"):
    _check(alert_type, alert_level)
    if USE_MOCK:
        d = _mock("vulnerability_stations.json")
        d["line"], d["alert_type"], d["alert_level"] = line, alert_type, alert_level
        return d
    from db import fetch_all
    rows = fetch_all(
        "SELECT s.station_name AS station, v.avg_delay, v.delay_rate, v.stop_rate, "
        "v.delta_delay, v.sample_n "
        "FROM station_vulnerability v JOIN stations s ON s.station_code=v.station_code "
        "WHERE s.line=%(line)s AND v.alert_type=%(at)s AND v.alert_level=%(al)s "
        "ORDER BY v.avg_delay DESC NULLS LAST",
        {"line": line, "at": alert_type, "al": alert_level},
    )
    return {"line": line, "alert_type": alert_type, "alert_level": alert_level, "stations": rows}


# ── GET /heatmap ──────────────────────────────────────────────
@app.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(line: str = "경부선", alert_type: str = "호우"):
    _check(alert_type)
    if USE_MOCK:
        d = _mock("heatmap.json")
        d["line"] = line
        return d
    from db import fetch_all
    # TODO(A와 확정): vuln(0~1) 의 정의. 아래는 avg_delay 를 min-max 정규화한 임시값.
    #   실제 취약도 점수 산식은 A(processor)가 정하면 그 컬럼을 읽도록 교체.
    nodes = fetch_all(
        "SELECT s.station_name AS station, s.lat, s.lon, v.avg_delay "
        "FROM stations s LEFT JOIN station_vulnerability v "
        "  ON v.station_code=s.station_code AND v.alert_type=%(at)s "
        "WHERE s.line=%(line)s ORDER BY s.seq_on_line NULLS LAST",
        {"line": line, "at": alert_type},
    )
    edges = fetch_all(
        'SELECT from_station AS "from", to_station AS "to", avg_delay_incr '
        "FROM segment_vulnerability WHERE line=%(line)s AND alert_type=%(at)s",
        {"line": line, "at": alert_type},
    )
    def norm(vals):
        xs = [x for x in vals if x is not None]
        lo, hi = (min(xs), max(xs)) if xs else (0, 1)
        span = (hi - lo) or 1
        return lo, span
    lo_n, sp_n = norm([r["avg_delay"] for r in nodes])
    lo_e, sp_e = norm([r["avg_delay_incr"] for r in edges])
    return {
        "line": line,
        "nodes": [{"station": r["station"], "lat": r["lat"], "lon": r["lon"],
                   "vuln": round(((r["avg_delay"] or lo_n) - lo_n) / sp_n, 3)} for r in nodes],
        "edges": [{"from": r["from"], "to": r["to"],
                   "vuln": round(((r["avg_delay_incr"] or lo_e) - lo_e) / sp_e, 3)} for r in edges],
    }


# ── GET /station/{code} (상세) ────────────────────────────────
@app.get("/station/{code}", response_model=StationDetail)
def get_station_detail(code: str):
    if USE_MOCK:
        # 정적 mock 없음: 스켈레톤에선 빈 상세를 계약 모양으로 반환.
        return {"station": code, "by_alert": [], "cases": []}
    from db import fetch_all
    by_alert = fetch_all(
        "SELECT alert_type, alert_level, avg_delay, sample_n "
        "FROM station_vulnerability WHERE station_code=%(c)s ORDER BY avg_delay DESC NULLS LAST",
        {"c": code},
    )
    # cases: 최근 지연 사례. 특보 종류 매칭은 A의 분석 영역이라 여기선 최근 지연만.
    cases = fetch_all(
        "SELECT run_date::text AS date, NULL::text AS alert_type, delay_min "
        "FROM train_stops WHERE station_code=%(c)s AND status='지연' "
        "ORDER BY event_time DESC LIMIT 10",
        {"c": code},
    )
    return {"station": code, "by_alert": by_alert, "cases": cases}


# ── GET /segment/{frm}/{to} (상세) ────────────────────────────
@app.get("/segment/{frm}/{to}", response_model=SegmentDetail)
def get_segment_detail(frm: str, to: str):
    if USE_MOCK:
        return {"from": frm, "to": to, "by_alert": [], "cases": []}
    from db import fetch_all
    by_alert = fetch_all(
        "SELECT alert_type, alert_level, avg_delay_incr AS avg_delay, sample_n "
        "FROM segment_vulnerability WHERE from_station=%(f)s AND to_station=%(t)s "
        "ORDER BY avg_delay_incr DESC NULLS LAST",
        {"f": frm, "t": to},
    )
    return {"from": frm, "to": to, "by_alert": by_alert, "cases": []}


# ── GET /checklist ────────────────────────────────────────────
@app.get("/checklist", response_model=ChecklistResponse)
def get_checklist(line: str = "경부선"):
    if USE_MOCK:
        d = _mock("checklist.json")
        d["line"] = line
        return d
    from db import fetch_all
    # 우선 점검 Top-N: 구간 취약도 상위. TODO(A와 확정): 현재 발효 특보 반영해 상단 가중.
    rows = fetch_all(
        "SELECT from_station, to_station, alert_type, alert_level, avg_delay_incr, sample_n "
        "FROM segment_vulnerability WHERE line=%(line)s "
        "ORDER BY avg_delay_incr DESC NULLS LAST LIMIT 10",
        {"line": line},
    )
    items = [{
        "rank": i + 1,
        "target": f"{r['from_station']}→{r['to_station']} 구간",
        "reason": f"{r['alert_type']} {r['alert_level']} 시 평균 +{r['avg_delay_incr']:.1f}분",
        "avg_delay_incr": r["avg_delay_incr"], "sample_n": r["sample_n"],
    } for i, r in enumerate(rows)]
    return {"line": line, "items": items}


# ── GET /alerts/active (실시간) ───────────────────────────────
@app.get("/alerts/active", response_model=AlertsActiveResponse, response_model_exclude_none=True)
def get_alerts_active(line: str = "경부선"):
    # exclude_none: affected 의 segment/station 은 서로 다른 키를 쓰므로(§5 예시),
    # 해당 없는 키(null)는 빼서 mock 파일·계약 예시와 완전히 같은 모양으로 응답한다.
    now = datetime.now(KST).isoformat(timespec="seconds")
    if USE_MOCK:
        d = _mock("alerts_active.json")
        d["line"], d["updated_at"] = line, now
        return d
    from db import fetch_all
    # 현재 발효 = end_time IS NULL (§1-1). 호우·폭염만.
    active_rows = fetch_all(
        "SELECT DISTINCT s.region_name, wa.alert_type, wa.alert_level, "
        "  MIN(wa.start_time) AS since, wa.region_code "
        "FROM weather_alerts wa JOIN stations s ON s.region_code=wa.region_code "
        "WHERE wa.end_time IS NULL AND wa.alert_type IN ('호우','폭염') AND s.line=%(line)s "
        "GROUP BY s.region_name, wa.alert_type, wa.alert_level, wa.region_code",
        {"line": line},
    )
    active = []
    for a in active_rows:
        # 그 구역에 걸린 취약 역. TODO(A와 확정): 구역→구간 귀속 규칙.
        affected_rows = fetch_all(
            "SELECT s.station_name AS station, v.avg_delay "
            "FROM station_vulnerability v JOIN stations s ON s.station_code=v.station_code "
            "WHERE s.region_code=%(rc)s AND v.alert_type=%(at)s "
            "ORDER BY v.avg_delay DESC NULLS LAST LIMIT 5",
            {"rc": a["region_code"], "at": a["alert_type"]},
        )
        affected = [{
            "type": "station", "station": r["station"], "vuln_rank": i + 1,
            "note": f"{a['alert_type']} {a['alert_level']} 시 평균 +{(r['avg_delay'] or 0):.1f}분",
        } for i, r in enumerate(affected_rows)]
        active.append({
            "region_name": a["region_name"], "alert_type": a["alert_type"],
            "alert_level": a["alert_level"],
            "since": a["since"].isoformat() if a["since"] else now,
            "affected": affected,
        })
    return {"line": line, "updated_at": now, "active": active}
