"""
api.py — B(백엔드) FastAPI. CONTRACT §5 를 그대로 노출한다.

두 가지 모드:
  USE_MOCK=1 (기본)  → mock/*.json 을 응답. A의 DB 없이도 오늘 바로 돌아가는 워킹 스켈레톤.
  USE_MOCK=0          → db.py 로 A가 채운 집계 테이블을 읽어 응답(읽기 전용).

두 모드 모두 **같은 계약 모양**으로 응답하므로, C 입장에선 URL도 안 바꾸고 넘어간다.
전환은 B가 환경변수 하나만 바꾸면 끝(§7 "URL만 교체"의 백엔드판).

응답 보장(§5-1): 키 항상 존재 / 빈 값은 [] · null / 순위는 취약도 내림차순 / 숫자는 숫자 /
지연=분, 비율=0~1 / 빈 데이터는 200+[], 오류만 4xx·5xx + {"error":{code,message}}.

── 이번 개정 요약 ────────────────────────────────────────────
- 삭제: GET /segment/{from}/{to}          → GET /segments/details?line= 로 대체
- 삭제: 모든 응답의 cases[] (과거 사례)   → 화면에서 제거됨
- 추가: station_id / segment_id / target_type
- 추가: GET /station/{station_id} 에 hourly_delay, alert_delay_comparison
- 강수량(rain_mm) · 예보(forecast) · 강풍 · 대설 은 모두 응답에 없다.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from models import (
    LinesResponse, SegmentsResponse, StationsResponse, HeatmapResponse,
    StationDetail, SegmentsDetailsResponse, ChecklistResponse, AlertsActiveResponse,
    station_slug, segment_slug, resolve_station,
)

# ── 설정 ──────────────────────────────────────────────────────
USE_MOCK = os.getenv("USE_MOCK", "1") == "1"
MOCK_DIR = Path(os.getenv("MOCK_DIR", Path(__file__).resolve().parent.parent / "mock"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
KST = timezone(timedelta(hours=9))

# 필터 허용값 (§5-1 (4)) — C가 자유 입력하지 않도록 B가 방어.
ALERT_TYPES = {"호우", "폭염"}   # 스코프 한정(CONTRACT §1: 호우·폭염만)
ALERT_LEVELS = {"주의보", "경보"}
TRAIN_TYPES = {"all", "KTX", "무궁화", "새마을"}

# 시간대 차트 버킷: 4시간 단위. 마지막 "24:00" 은 축을 닫기 위한 00:00 의 사본.
HOUR_BUCKETS = [0, 4, 8, 12, 16, 20]

app = FastAPI(title="경부선 기상 취약구간 API", version="0.2.0")
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


def _r1(v) -> float | None:
    """소수 1자리 반올림. None 은 None 그대로(표본 없음 ≠ 0)."""
    return None if v is None else round(float(v), 1)


def _bucket_rows_to_points(rows: list[dict], *keys: str) -> list[dict]:
    """{bucket: 0|4|…|20} 행들을 "00:00"~"24:00" 7포인트로 편다. 없는 버킷은 null."""
    by_bucket = {int(r["bucket"]): r for r in rows}
    points = []
    for h in HOUR_BUCKETS + [0]:          # 마지막 0 → "24:00" 으로 표기
        r = by_bucket.get(h, {})
        p = {"time": f"{h:02d}:00"}
        p.update({k: _r1(r.get(k)) for k in keys})
        points.append(p)
    points[-1]["time"] = "24:00"
    return points


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
        for s in d["segments"]:
            s.setdefault("segment_id", segment_slug(s["from"], s["to"]))
        return d
    from db import fetch_all
    # NOTE(계약 갭): 현재 segment_vulnerability(§4)에는 train_type 컬럼이 없다.
    # train_type 필터는 A가 집계에 차원을 추가해야 실제 동작한다. 지금은 무시(all 취급).
    rows = fetch_all(
        # segment_vulnerability.from_station/to_station 은 역 '코드'(stations FK)다.
        # 계약 §5 는 역 '이름'("대전")을 요구하므로 JOIN 으로 변환한다.
        # (station_vulnerability 조회와 같은 방식. 변환 없이 내보내면 segment_id 도
        #  '3900895-3900114' 가 되어 C의 상세 링크가 깨진다.)
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "v.avg_delay_incr, v.stop_rate, v.sample_n "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        "WHERE v.line=%(line)s AND v.alert_type=%(at)s AND v.alert_level=%(al)s "
        "ORDER BY v.avg_delay_incr DESC NULLS LAST",
        {"line": line, "at": alert_type, "al": alert_level},
    )
    segments = [{**r, "segment_id": segment_slug(r["from"], r["to"])} for r in rows]
    return {"line": line, "alert_type": alert_type, "alert_level": alert_level, "segments": segments}


# ── GET /vulnerability/stations ───────────────────────────────
@app.get("/vulnerability/stations", response_model=StationsResponse)
def get_stations(line: str = "경부선", alert_type: str = "폭염", alert_level: str = "경보"):
    _check(alert_type, alert_level)
    if USE_MOCK:
        d = _mock("vulnerability_stations.json")
        d["line"], d["alert_type"], d["alert_level"] = line, alert_type, alert_level
        for s in d["stations"]:
            s.setdefault("station_id", station_slug(s["station"]))
            # mock 에 delay_count 가 없으면 sample_n * delay_rate 로 유도(프론트 추정식과 동일).
            if s.get("delay_count") is None and s.get("sample_n") is not None \
                    and s.get("delay_rate") is not None:
                s["delay_count"] = round(s["sample_n"] * s["delay_rate"])
        return d
    from db import fetch_all
    rows = fetch_all(
        "SELECT s.station_name AS station, v.avg_delay, v.delay_rate, v.stop_rate, "
        "v.delta_delay, v.sample_n, "
        # delay_count 컬럼은 없다. sample_n * delay_rate 를 반올림해 유도(프론트 추정식과 동일).
        "ROUND(v.sample_n * v.delay_rate)::int AS delay_count "
        "FROM station_vulnerability v JOIN stations s ON s.station_code=v.station_code "
        "WHERE s.line=%(line)s AND v.alert_type=%(at)s AND v.alert_level=%(al)s "
        "ORDER BY v.avg_delay DESC NULLS LAST",
        {"line": line, "at": alert_type, "al": alert_level},
    )
    stations = [{**r, "station_id": station_slug(r["station"])} for r in rows]
    return {"line": line, "alert_type": alert_type, "alert_level": alert_level, "stations": stations}


# ── GET /heatmap ──────────────────────────────────────────────
@app.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(line: str = "경부선", alert_type: str | None = None):
    """노선 히트맵.

    alert_type 을 주면 그 특보만, **생략하면 호우·폭염을 합쳐서** 본다(기본).
    합치는 이유: 어떤 역은 호우 이력만, 어떤 역은 폭염 이력만 있다.
    한 종류로 고정하면 다른 종류만 겪은 역이 '데이터 없음'으로 빠져
    노선 전체를 한눈에 본다는 히트맵의 목적이 깨진다.
    """
    if alert_type is not None:
        _check(alert_type)
    if USE_MOCK:
        d = _mock("heatmap.json")
        d["line"] = line
        return d
    from db import fetch_all
    # TODO(확정 필요): vuln(0~1) 의 정의. 아래는 avg_delay 를 min-max 정규화한 임시값.
    #   실제 취약도 점수 산식이 정해지면 그 컬럼을 읽도록 교체.
    #
    # alert_type 이 없으면 스코프 전체(호우·폭염)를 대상으로 한다.
    at_filter = "v.alert_type = %(at)s" if alert_type else "v.alert_type IN ('호우','폭염')"
    params = {"line": line}
    if alert_type:
        params["at"] = alert_type

    nodes = fetch_all(
        # ⚠️ station_vulnerability 의 PK 는 (station_code, alert_type, alert_level) 다.
        #    종류·등급 조건 없이 JOIN 하면 여러 행이 붙어 역이 '중복 노드'로 나온다.
        #    히트맵은 역당 한 점이므로 MAX 로 합친다.
        #    MAX = 그 조건에서 겪은 '최악'의 평균지연 → 취약도 표시 목적에 맞다.
        "SELECT s.station_name AS station, s.lat, s.lon, MAX(v.avg_delay) AS avg_delay "
        "FROM stations s LEFT JOIN station_vulnerability v "
        f"  ON v.station_code=s.station_code AND {at_filter} "
        "WHERE s.line=%(line)s "
        "GROUP BY s.station_name, s.lat, s.lon, s.seq_on_line "
        "ORDER BY s.seq_on_line NULLS LAST",
        params,
    )
    edges = fetch_all(
        # nodes 와 같은 이유로 중복이 생긴다 → MAX 로 합친다.
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  MAX(v.avg_delay_incr) AS avg_delay_incr "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        f"WHERE v.line=%(line)s AND {at_filter} "
        "GROUP BY sf.station_name, st.station_name",
        params,
    )
    def norm(vals):
        xs = [x for x in vals if x is not None]
        lo, hi = (min(xs), max(xs)) if xs else (0, 1)
        span = (hi - lo) or 1
        return lo, span
    lo_n, sp_n = norm([r["avg_delay"] for r in nodes])
    lo_e, sp_e = norm([r["avg_delay_incr"] for r in edges])

    def scale(v, lo, span):
        # 계약 §5-1(2)·§2-1(3): 표본 없음은 null(=데이터 없음). 0.0(취약도 낮음)과 구분해야 한다.
        # (v or lo) 로 NULL 을 최솟값으로 대체하면 '데이터 없음'과 '가장 덜 취약'이 뭉개진다.
        return None if v is None else round((v - lo) / span, 3)

    return {
        "line": line,
        "nodes": [{"station": r["station"], "lat": r["lat"], "lon": r["lon"],
                   "vuln": scale(r["avg_delay"], lo_n, sp_n)} for r in nodes],
        "edges": [{"from": r["from"], "to": r["to"],
                   "vuln": scale(r["avg_delay_incr"], lo_e, sp_e)} for r in edges],
    }


# ── GET /station/{station_id} (역 상세) ───────────────────────
@app.get("/station/{station_id}", response_model=StationDetail)
def get_station_detail(station_id: str):
    """station_id 는 슬러그(daejeon). 역명(대전)으로 불러도 동작한다."""
    station_name = resolve_station(station_id)

    if USE_MOCK:
        d = _mock("station_details.json")
        d["station"] = station_name   # 어떤 역을 조회하든 상세 모양을 보여준다(값은 mock)
        d["station_id"] = station_slug(station_name)
        # 스코프 밖 특보(강풍·대설)가 mock 에 남아 있어도 응답에서는 걸러낸다.
        d["alert_delay_comparison"] = [
            c for c in d.get("alert_delay_comparison", []) if c.get("alert_type") in ALERT_TYPES
        ]
        d["by_alert"] = [b for b in d.get("by_alert", []) if b.get("alert_type") in ALERT_TYPES]
        return d

    from db import fetch_all, fetch_one
    # 계약 §5의 다른 응답은 모두 역'이름'을 쓴다("station": "대전").
    # station_vulnerability 는 역'코드'로 저장되므로 이름·코드·슬러그 어느 쪽이 와도 해석한다.
    row = fetch_one(
        "SELECT station_code, station_name FROM stations "
        "WHERE station_name=%(c)s OR station_code=%(c)s LIMIT 1",
        {"c": station_name},
    )
    if row is None:
        raise AppError(404, "STATION_NOT_FOUND", f"알 수 없는 역: {station_id}")
    station_code, station_name = row["station_code"], row["station_name"]

    by_alert = fetch_all(
        "SELECT alert_type, alert_level, avg_delay, sample_n "
        "FROM station_vulnerability "
        "WHERE station_code=%(c)s AND alert_type IN ('호우','폭염') "
        "ORDER BY avg_delay DESC NULLS LAST",
        {"c": station_code},
    )

    # 시간대별 지연: event_time(예정 도착) 4시간 버킷, KST. 주말=holiday.
    # 공휴일 달력이 없으므로 '휴일'은 토·일만 뜻한다(모델 주석 참고).
    hourly_rows = fetch_all(
        "SELECT (EXTRACT(HOUR FROM event_time AT TIME ZONE 'Asia/Seoul')::int / 4) * 4 AS bucket, "
        "  AVG(delay_min) FILTER "
        "    (WHERE EXTRACT(ISODOW FROM event_time AT TIME ZONE 'Asia/Seoul') < 6) AS weekday_delay, "
        "  AVG(delay_min) FILTER "
        "    (WHERE EXTRACT(ISODOW FROM event_time AT TIME ZONE 'Asia/Seoul') >= 6) AS holiday_delay "
        "FROM train_stops "
        "WHERE station_code=%(c)s AND delay_min IS NOT NULL "
        "GROUP BY 1 ORDER BY 1",
        {"c": station_code},
    )
    hourly_delay = _bucket_rows_to_points(hourly_rows, "weekday_delay", "holiday_delay")

    # 평시 vs 특보(경보) 평균 지연 비교. 호우·폭염 2행 고정 — 표본 없으면 null.
    cmp_rows = fetch_all(
        "SELECT alert_type, base_avg_delay, avg_delay FROM station_vulnerability "
        "WHERE station_code=%(c)s AND alert_level='경보' AND alert_type IN ('호우','폭염')",
        {"c": station_code},
    )
    cmp_by_type = {r["alert_type"]: r for r in cmp_rows}
    alert_delay_comparison = [
        {
            "alert_type": t,
            "normal_avg_delay": _r1(cmp_by_type.get(t, {}).get("base_avg_delay")),
            "alert_avg_delay": _r1(cmp_by_type.get(t, {}).get("avg_delay")),
        }
        for t in ("호우", "폭염")
    ]

    return {
        "station_id": station_slug(station_name),
        "station": station_name,
        "by_alert": by_alert,
        "hourly_delay": hourly_delay,
        "alert_delay_comparison": alert_delay_comparison,
    }


# ── GET /segments/details (구간 상세 번들) ───────────────────
# 구(舊) GET /segment/{from}/{to} 대체. C는 이 번들 하나를 받아 segment_id 로 찾는다.
@app.get("/segments/details", response_model=SegmentsDetailsResponse)
def get_segments_details(line: str = "경부선"):
    if USE_MOCK:
        d = _mock("segments_details.json")
        d["line"] = line
        for s in d["segments"]:
            s.setdefault("segment_id", segment_slug(s["from"], s["to"]))
            # 스코프 밖 특보 행 제거. 강수량·사례는 응답 모델이 알아서 버린다.
            s["by_alert"] = [b for b in s.get("by_alert", []) if b.get("alert_type") in ALERT_TYPES]
            # mock 에 남아 있는 type="forecast" 포인트를 실적으로 표기한다.
            # (mock 값은 어차피 전부 가짜다. 예보를 만들지 않는다는 계약만 지키면 된다.)
            for p in s.get("hourly_delay", []):
                p["type"] = "actual"
        return d

    from db import fetch_all
    # 구간 신규 지연(§4 참고 SQL). 인접 seq(A→B)의 delay_min 차.
    # 읽기 전용이라 매 요청 계산한다. 무거워지면 A에게 segment_daily 집계 테이블을 요청한다.
    INCR_CTE = (
        "WITH incr AS ( "
        "  SELECT a.station_code AS f, b.station_code AS t, "
        "         b.delay_min - a.delay_min AS delay_incr, b.event_time "
        "  FROM train_stops a JOIN train_stops b "
        "    ON a.run_date=b.run_date AND a.train_no=b.train_no AND b.seq=a.seq+1 "
        "  WHERE a.line=%(line)s AND a.delay_min IS NOT NULL AND b.delay_min IS NOT NULL "
        ") "
    )

    vuln_rows = fetch_all(
        # 코드 → 이름 JOIN. 아래 hourly_rows·trend_rows 가 이미 station_name 으로
        # 키를 만드므로, 여기서도 이름으로 맞춰야 key(r) 매칭이 성립한다.
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  v.alert_type, v.alert_level, v.avg_delay_incr, v.stop_rate, v.sample_n "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        "WHERE v.line=%(line)s AND v.alert_type IN ('호우','폭염') "
        "ORDER BY v.avg_delay_incr DESC NULLS LAST",
        {"line": line},
    )

    hourly_rows = fetch_all(
        INCR_CTE +
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  (EXTRACT(HOUR FROM i.event_time AT TIME ZONE 'Asia/Seoul')::int / 4) * 4 AS bucket, "
        "  AVG(i.delay_incr) AS delay_min "
        "FROM incr i "
        "  JOIN stations sf ON sf.station_code=i.f "
        "  JOIN stations st ON st.station_code=i.t "
        "GROUP BY 1,2,3",
        {"line": line},
    )

    trend_rows = fetch_all(
        INCR_CTE +
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  (i.event_time AT TIME ZONE 'Asia/Seoul')::date::text AS date, "
        "  AVG(i.delay_incr) AS delay_increase "
        "FROM incr i "
        "  JOIN stations sf ON sf.station_code=i.f "
        "  JOIN stations st ON st.station_code=i.t "
        "WHERE i.event_time >= now() - interval '7 days' "
        "GROUP BY 1,2,3 ORDER BY 3",
        {"line": line},
    )

    def key(r):
        return (r["from"], r["to"])

    seg_keys, seen = [], set()
    for r in vuln_rows:                       # 취약도 높은 순 유지(§5-1(2) 정렬 보장)
        if key(r) not in seen:
            seen.add(key(r))
            seg_keys.append(key(r))

    segments = []
    for frm, to in seg_keys:
        buckets = [r for r in hourly_rows if key(r) == (frm, to)]
        segments.append({
            "segment_id": segment_slug(frm, to),
            "from": frm,
            "to": to,
            "hourly_delay": _bucket_rows_to_points(buckets, "delay_min"),
            "delay_increase_trend": [
                {"date": r["date"], "delay_increase": _r1(r["delay_increase"])}
                for r in trend_rows if key(r) == (frm, to)
            ],
            "by_alert": [
                {
                    "alert_type": r["alert_type"], "alert_level": r["alert_level"],
                    # TODO(A): segment_vulnerability 에 avg_delay(도착역 절대 지연) 컬럼 추가 요청.
                    #   추가 전까지 null. 키는 항상 존재한다(§5-1(2)).
                    "avg_delay": None,
                    "delay_increase": r["avg_delay_incr"],
                    "stop_rate": r["stop_rate"], "sample_n": r["sample_n"],
                }
                for r in vuln_rows if key(r) == (frm, to)
            ],
        })
    return {"line": line, "segments": segments}


# ── GET /checklist ────────────────────────────────────────────
@app.get("/checklist", response_model=ChecklistResponse, response_model_exclude_none=True)
def get_checklist(line: str = "경부선"):
    if USE_MOCK:
        d = _mock("checklist.json")
        d["line"] = line
        return d
    from db import fetch_all
    # 우선 점검 Top-N: 구간 취약도 상위. TODO(A와 확정): 현재 발효 특보 반영해 상단 가중.
    rows = fetch_all(
        # 코드 → 이름 JOIN. 이름이라야 target("대전→김천(구미) 구간")과 segment_id 가 맞다.
        "SELECT sf.station_name AS from_station, st.station_name AS to_station, "
        "  v.alert_type, v.alert_level, v.avg_delay_incr, v.sample_n "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        "WHERE v.line=%(line)s AND v.alert_type IN ('호우','폭염') "
        "ORDER BY v.avg_delay_incr DESC NULLS LAST LIMIT 10",
        {"line": line},
    )
    items = [{
        "rank": i + 1,
        "target_type": "segment",
        "segment_id": segment_slug(r["from_station"], r["to_station"]),
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
    # region_code 기준으로 묶는다. 한 특보구역에 여러 region_name 이 매핑될 수 있어
    # (예: 같은 구역코드에 '김천'·'대구'), region_name 으로 묶으면 특보 1건이 중복 노출된다.
    active_rows = fetch_all(
        "SELECT wa.region_code, MIN(s.region_name) AS region_name, "
        "  wa.alert_type, wa.alert_level, MIN(wa.start_time) AS since "
        "FROM weather_alerts wa JOIN stations s ON s.region_code=wa.region_code "
        "WHERE wa.end_time IS NULL AND wa.alert_type IN ('호우','폭염') AND s.line=%(line)s "
        "GROUP BY wa.region_code, wa.alert_type, wa.alert_level",
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
            # 계약 §2-1(2): 모든 시각은 KST 로 표기. psycopg 는 TIMESTAMPTZ 를 UTC 로 돌려주므로 변환.
            "since": a["since"].astimezone(KST).isoformat(timespec="seconds") if a["since"] else now,
            "affected": affected,
        })
    return {"line": line, "updated_at": now, "active": active}
