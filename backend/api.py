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
from risk_rules import (
    classify_station_risk, classify_segment_risk, get_confidence,
    station_risk_reason, segment_risk_reason,
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


# ── 등급 부착 ────────────────────────────────────────────────
# 원시 지표 dict 에 risk_level/confidence/risk_reason 을 채운다(mock·DB 공용).
# 프론트가 자체 임계값을 계산하지 않도록 백엔드가 단일 기준으로 등급을 확정한다.
def _attach_station_risk(item: dict) -> dict:
    n = item.get("sample_n") or 0
    lvl = classify_station_risk(item.get("delta_delay"), item.get("delay_rate"), n)
    item["risk_level"] = lvl
    item["confidence"] = get_confidence(n)
    item["risk_reason"] = station_risk_reason(
        lvl, item.get("delta_delay"), item.get("delay_rate"), n)
    return item


def _attach_segment_risk(item: dict) -> dict:
    n = item.get("sample_n") or 0
    lvl = classify_segment_risk(item.get("avg_delay_incr"), n)
    item["risk_level"] = lvl
    item["confidence"] = get_confidence(n)
    item["risk_reason"] = segment_risk_reason(lvl, item.get("avg_delay_incr"), n)
    return item


# 히트맵 vuln(0~1) ↔ 등급. 등급이 권위값, vuln 은 하위호환 색상 힌트.
_VULN_BY_RISK = {"high": 0.85, "warning": 0.6, "interest": 0.2, "insufficient": None}


def _vuln_to_risk(vuln) -> str:
    """mock 노드가 risk_level 없이 vuln 만 있을 때의 역산(설명용 fallback)."""
    if vuln is None:
        return "insufficient"
    v = float(vuln)
    if v >= 0.7:
        return "high"
    if v >= 0.5:
        return "warning"
    return "interest"


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
def get_segments(line: str = "경부선", alert_type: str | None = None,
                 alert_level: str | None = None, train_type: str | None = None):
    """구간별 취약도.

    alert_type·alert_level 을 주면 그 조합만, **생략하면 전체를 합쳐서** 본다
    (/vulnerability/stations, /heatmap 과 같은 규칙).
    예전엔 기본값이 호우·경보로 고정이라, 프론트에서 '전체'를 골라도
    호우 경보만 나오고 다른 조합은 보이지 않았다.
    """
    _check(alert_type, alert_level, train_type)
    if USE_MOCK:
        d = _mock("vulnerability_segments.json")
        d["line"] = line
        d["alert_type"] = alert_type or "전체"
        d["alert_level"] = alert_level or "전체"
        for s in d["segments"]:
            s.setdefault("segment_id", segment_slug(s["from"], s["to"]))
            _attach_segment_risk(s)
        return d
    from db import fetch_all

    conds = ["v.line = %(line)s"]
    params = {"line": line}
    if alert_type:
        conds.append("v.alert_type = %(at)s")
        params["at"] = alert_type
    else:
        conds.append("v.alert_type IN ('호우','폭염')")
    if alert_level:
        conds.append("v.alert_level = %(al)s")
        params["al"] = alert_level
    where = " AND ".join(conds)

    # NOTE(계약 갭): segment_vulnerability 에는 train_type 차원이 없다.
    #   지금은 KTX 만 수집하므로 필터를 받아도 결과가 같다. 무궁화·ITX 를 추가할 때
    #   집계 테이블에 train_type 컬럼을 넣고 여기에 조건을 붙인다.
    #
    # 여러 조합을 합칠 땐 표본수 가중평균(단순 평균은 표본 적은 조합을 과대평가).
    rows = fetch_all(
        # from_station/to_station 은 역 '코드'다. 계약은 역 '이름'을 요구하므로 JOIN 으로 변환한다.
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  SUM(v.avg_delay_incr * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS avg_delay_incr, "
        "  SUM(v.stop_rate      * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS stop_rate, "
        "  SUM(v.sample_n) AS sample_n "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        f"WHERE {where} "
        'GROUP BY sf.station_name, st.station_name '
        "ORDER BY 3 DESC NULLS LAST",
        params,
    )
    segments = [_attach_segment_risk({
        "segment_id": segment_slug(r["from"], r["to"]),
        "from": r["from"], "to": r["to"],
        "avg_delay_incr": _r1(r["avg_delay_incr"]),
        "stop_rate": round(r["stop_rate"], 2) if r["stop_rate"] is not None else None,
        "sample_n": r["sample_n"],
    }) for r in rows]
    return {
        "line": line,
        "alert_type": alert_type or "전체",
        "alert_level": alert_level or "전체",
        "segments": segments,
    }


# ── GET /vulnerability/stations ───────────────────────────────
@app.get("/vulnerability/stations", response_model=StationsResponse)
def get_stations(line: str = "경부선", alert_type: str | None = None, alert_level: str | None = None):
    """역별 취약도.

    alert_type·alert_level 을 주면 그 조합만, **생략하면 전체를 합쳐서** 본다.
    합치는 이유: 어떤 역은 폭염 주의보 이력만 있다(예: 울산 751건, 폭염 경보 0건).
    한 조합으로 고정하면 그런 역이 통째로 '정보 없음'이 되어, 역 상세의
    카드 4개가 전부 '-' 로 나온다(차트는 등급을 합치므로 값이 나오는데도).
    """
    _check(alert_type, alert_level)
    if USE_MOCK:
        d = _mock("vulnerability_stations.json")
        d["line"] = line
        d["alert_type"] = alert_type or "전체"
        d["alert_level"] = alert_level or "전체"
        for s in d["stations"]:
            s.setdefault("station_id", station_slug(s["station"]))
            if s.get("delay_count") is None and s.get("sample_n") is not None \
                    and s.get("delay_rate") is not None:
                s["delay_count"] = round(s["sample_n"] * s["delay_rate"])
            _attach_station_risk(s)
        return d
    from db import fetch_all

    # 조건을 선택적으로 붙인다. 값 자체는 플레이스홀더로만 전달한다(인젝션 방지).
    conds = ["s.line = %(line)s"]
    params = {"line": line}
    if alert_type:
        conds.append("v.alert_type = %(at)s")
        params["at"] = alert_type
    else:
        conds.append("v.alert_type IN ('호우','폭염')")
    if alert_level:
        conds.append("v.alert_level = %(al)s")
        params["al"] = alert_level
    where = " AND ".join(conds)

    # 여러 조합을 합칠 땐 표본수 가중평균을 쓴다.
    # 단순 평균이면 표본 6건짜리 주의보가 644건짜리 경보와 같은 무게를 갖는다.
    # base_avg_delay 는 역 단위 기준선이라 조합과 무관하게 같은 값 → MAX 로 집어온다.
    rows = fetch_all(
        "SELECT s.station_name AS station, "
        "  SUM(v.avg_delay  * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS avg_delay, "
        "  SUM(v.delay_rate * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS delay_rate, "
        "  SUM(v.stop_rate  * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS stop_rate, "
        "  MAX(v.base_avg_delay) AS base_avg_delay, "
        "  SUM(v.sample_n) AS sample_n "
        "FROM station_vulnerability v JOIN stations s ON s.station_code=v.station_code "
        f"WHERE {where} "
        "GROUP BY s.station_name "
        "ORDER BY 2 DESC NULLS LAST",
        params,
    )
    stations = []
    for r in rows:
        avg = _r1(r["avg_delay"])
        base = _r1(r["base_avg_delay"])
        n = r["sample_n"]
        rate = r["delay_rate"]
        stations.append(_attach_station_risk({
            "station_id": station_slug(r["station"]),
            "station": r["station"],
            "avg_delay": avg,
            "delay_rate": round(rate, 2) if rate is not None else None,
            "stop_rate": round(r["stop_rate"], 2) if r["stop_rate"] is not None else None,
            "delta_delay": _r1((avg - base) if (avg is not None and base is not None) else None),
            "sample_n": n,
            # delay_count 는 DB 컬럼이 아니라 유도값(프론트 추정식과 동일)
            "delay_count": round(n * rate) if (n is not None and rate is not None) else None,
        }))
    return {
        "line": line,
        "alert_type": alert_type or "전체",
        "alert_level": alert_level or "전체",
        "stations": stations,
    }


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
        for it in d.get("nodes", []) + d.get("edges", []):
            it.setdefault("risk_level", _vuln_to_risk(it.get("vuln")))
        return d
    from db import fetch_all
    # alert_type 이 없으면 스코프 전체(호우·폭염)를 대상으로 한다.
    at_filter = "v.alert_type = %(at)s" if alert_type else "v.alert_type IN ('호우','폭염')"
    params = {"line": line}
    if alert_type:
        params["at"] = alert_type

    nodes = fetch_all(
        # ⚠️ station_vulnerability 의 PK 는 (station_code, alert_type, alert_level) 다.
        #    종류·등급 조건 없이 JOIN 하면 여러 행이 붙어 역이 '중복 노드'로 나온다.
        #    히트맵은 역당 한 점이므로 합친다. 예전엔 MAX(최악값)를 썼으나, 순위표는
        #    표본수 가중평균을 써서 같은 역이 노선도 '높음' / 순위표 '관심'으로 어긋났다.
        #    → 순위표와 동일하게 표본수 가중평균으로 합쳐 등급을 일치시킨다.
        #
        # 역 등급은 delta_delay(평시 대비 증가) + delay_rate 2지표를 함께 본다.
        # 그래서 delay_rate 뿐 아니라 avg_delay·base_avg_delay·sample_n 도 가져온다.
        # base_avg_delay 는 역 단위 기준선이라 조합과 무관하게 같은 값 → MAX 로 집어온다.
        "SELECT s.station_name AS station, s.lat, s.lon, "
        "  SUM(v.delay_rate * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS delay_rate, "
        "  SUM(v.avg_delay  * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS avg_delay, "
        "  MAX(v.base_avg_delay) AS base_avg_delay, "
        "  SUM(v.sample_n) AS sample_n "
        "FROM stations s LEFT JOIN station_vulnerability v "
        f"  ON v.station_code=s.station_code AND {at_filter} "
        "WHERE s.line=%(line)s "
        "GROUP BY s.station_name, s.lat, s.lon, s.seq_on_line "
        "ORDER BY s.seq_on_line NULLS LAST",
        params,
    )
    edges = fetch_all(
        # nodes 와 같은 이유로 중복이 생긴다 → 순위표와 같은 표본수 가중평균으로 합친다.
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  SUM(v.avg_delay_incr * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS avg_delay_incr, "
        "  SUM(v.sample_n) AS sample_n "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        f"WHERE v.line=%(line)s AND {at_filter} "
        "GROUP BY sf.station_name, st.station_name",
        params,
    )

    # ── 등급 → vuln(0~1) ─────────────────────────────────────────
    # 등급 산정을 risk_rules 로 단일화했으므로, 예전의 임의 0~1 선형 변환(_abs_vuln)은 버린다.
    # vuln 은 하위호환 색상 힌트로만 남기고 risk_level 에서 파생시켜 둘이 항상 일치하게 한다.
    #   높음 0.85 / 주의 0.6 / 관심 0.2 / 표본부족 → null(표본 없음과 동일 취급).
    # (프론트 현행 임계값 0.7·0.5 로도 색이 올바르게 나온다.)
    def _node(r):
        n = r["sample_n"] or 0
        delta = None
        if r["avg_delay"] is not None and r["base_avg_delay"] is not None:
            delta = round(float(r["avg_delay"]) - float(r["base_avg_delay"]), 1)
        lvl = classify_station_risk(delta, r["delay_rate"], n)
        return {"station": r["station"], "lat": r["lat"], "lon": r["lon"],
                "vuln": _VULN_BY_RISK[lvl], "risk_level": lvl}

    def _edge(r):
        n = r["sample_n"] or 0
        lvl = classify_segment_risk(r["avg_delay_incr"], n)
        return {"from": r["from"], "to": r["to"],
                "vuln": _VULN_BY_RISK[lvl], "risk_level": lvl}

    return {
        "line": line,
        "nodes": [_node(r) for r in nodes],
        "edges": [_edge(r) for r in edges],
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

    # 평시 vs 특보 시 평균 지연 비교. 호우·폭염 2행 고정 — 표본 없으면 null.
    #
    # ⚠️ 등급(주의보/경보)을 가리지 않고 합친다.
    #    이 응답에는 alert_level 필드가 없다 — "평시 vs **특보**" 비교이지 등급별이 아니다.
    #    경보만 보면 주의보 이력만 있는 역(예: 호우 주의보만 겪은 김천구미·동대구)이
    #    빈 그래프가 된다. 실제로 그렇게 나왔다.
    #
    #    합치는 방식은 표본수 가중평균: SUM(avg_delay × sample_n) / SUM(sample_n).
    #    단순 평균을 쓰면 표본 6건짜리 주의보와 500건짜리 경보가 같은 무게를 갖는다.
    #    base_avg_delay 는 역 단위 기준선이라 등급과 무관하게 같은 값 → MAX 로 집어온다.
    cmp_rows = fetch_all(
        "SELECT alert_type, "
        "  MAX(base_avg_delay) AS base_avg_delay, "
        "  SUM(avg_delay * sample_n) / NULLIF(SUM(sample_n), 0) AS avg_delay "
        "FROM station_vulnerability "
        "WHERE station_code=%(c)s AND alert_type IN ('호우','폭염') "
        "GROUP BY alert_type",
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
    # ⚠️ 이 CTE 는 processor/vulnerability.py 의 구간 정의와 **반드시 같아야 한다.**
    #    by_alert 은 segment_vulnerability(집계 테이블)에서 오고, hourly/trend 는 여기서 온다.
    #    정의가 다르면 같은 응답 안에서 두 지표가 어긋나거나 키가 안 맞아 통째로 누락된다.
    #
    #    맞춰야 할 두 가지:
    #    (1) 인접: seq(열차 정차순서)만 쓰면 KTX 가 역을 건너뛸 때(서울→오송 급행)
    #        선로에 없는 구간이 생긴다. seq_on_line 차이가 1 인 것만 인정한다.
    #    (2) 정규화: from/to 를 노선 순서(북→남)로 통일한다. 정규화하지 않으면
    #        상행(부산→울산)이 집계의 '울산-부산' 과 키가 달라 매칭에 실패한다.
    INCR_CTE = (
        "WITH incr AS ( "
        "  SELECT "
        "    CASE WHEN sa.seq_on_line < sb.seq_on_line THEN a.station_code "
        "         ELSE b.station_code END AS f, "
        "    CASE WHEN sa.seq_on_line < sb.seq_on_line THEN b.station_code "
        "         ELSE a.station_code END AS t, "
        "    b.delay_min - a.delay_min AS delay_incr, "
        "    b.event_time "
        "  FROM train_stops a "
        "  JOIN train_stops b "
        "    ON a.run_date=b.run_date AND a.train_no=b.train_no AND b.seq=a.seq+1 "
        "  JOIN stations sa ON sa.station_code=a.station_code "
        "  JOIN stations sb ON sb.station_code=b.station_code "
        "  WHERE a.delay_min IS NOT NULL AND b.delay_min IS NOT NULL "
        "    AND sa.line=%(line)s AND sb.line=%(line)s "
        "    AND ABS(sa.seq_on_line - sb.seq_on_line) = 1 "
        ") "
    )

    vuln_rows = fetch_all(
        # 코드 → 이름 JOIN. 아래 hourly_rows·trend_rows 가 이미 station_name 으로
        # 키를 만드므로, 여기서도 이름으로 맞춰야 key(r) 매칭이 성립한다.
        'SELECT sf.station_name AS "from", st.station_name AS "to", '
        "  v.alert_type, v.alert_level, v.avg_delay_incr, v.avg_delay, "
        "  v.delay_rate, v.stop_rate, v.sample_n "
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
                    # avg_delay = 도착역 절대 지연, delay_increase = 이 구간에서 새로 생긴 지연.
                    # 둘은 다른 지표다. 구간 상세는 둘 다 보여준다.
                    "avg_delay": _r1(r["avg_delay"]),
                    "delay_rate": r["delay_rate"],
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
        for it in d.get("items", []):
            it.setdefault("risk_level",
                          classify_segment_risk(it.get("avg_delay_incr"), it.get("sample_n") or 0))
        return d
    from db import fetch_all
    # 우선 점검 Top-N. 등급이 순위표·히트맵과 어긋나지 않도록 **같은 집계 단위**를 쓴다:
    #   특보 조합별 행이 아니라 '구간 단위'로 표본수 가중평균을 낸 뒤 등급을 매긴다.
    #   (조합별로 매기면 한 특보에서만 심한 구간이 checklist 에서만 주의로 뜬다.)
    # TODO(A와 확정): 현재 발효 특보 반영해 상단 가중.
    rows = fetch_all(
        # 코드 → 이름 JOIN. 이름이라야 target("대전→김천구미 구간")과 segment_id 가 맞다.
        # get_segments 와 동일한 가중평균. 표본 적은 조합이 과대평가되지 않는다.
        'SELECT sf.station_name AS from_station, st.station_name AS to_station, '
        "  SUM(v.avg_delay_incr * v.sample_n) / NULLIF(SUM(v.sample_n),0) AS avg_delay_incr, "
        "  SUM(v.sample_n) AS sample_n "
        "FROM segment_vulnerability v "
        "  JOIN stations sf ON sf.station_code=v.from_station "
        "  JOIN stations st ON st.station_code=v.to_station "
        "WHERE v.line=%(line)s AND v.alert_type IN ('호우','폭염') "
        "GROUP BY sf.station_name, st.station_name",
        {"line": line},
    )
    # 1) 표본 10건 미만 제외  2) 등급(높음→주의→관심) 우선  3) 같은 등급이면 신규지연 내림차순  4) 상위 10
    _RISK_ORDER = {"high": 0, "warning": 1, "interest": 2, "insufficient": 3}
    cands = []
    for r in rows:
        n = r["sample_n"] or 0
        if n < 10:
            continue
        lvl = classify_segment_risk(r["avg_delay_incr"], n)
        cands.append((lvl, r))
    cands.sort(key=lambda t: (_RISK_ORDER[t[0]], -(t[1]["avg_delay_incr"] or 0)))
    items = [{
        "rank": i + 1,
        "target_type": "segment",
        "segment_id": segment_slug(r["from_station"], r["to_station"]),
        "target": f"{r['from_station']}→{r['to_station']} 구간",
        # 조합이 아니라 구간 전체 기준 사유(등급과 같은 근거).
        "reason": segment_risk_reason(lvl, r["avg_delay_incr"], r["sample_n"]),
        "avg_delay_incr": _r1(r["avg_delay_incr"]), "sample_n": r["sample_n"],
        "risk_level": lvl,
    } for i, (lvl, r) in enumerate(cands[:10])]
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
    # ⚠️ 역↔특보구역은 반드시 station_regions(1:N)로 잇는다.
    #    stations.region_code 는 '대표 구역' 1개뿐이라, 다른 하위구역으로 발령된 특보를
    #    놓친다(예: 부산역 대표=L1082600 부산중부인데 L1082500 부산동부로 발령).
    #    그러면 vulnerability.py(station_regions 사용)에는 잡힌 특보가
    #    현재 특보 화면에는 안 뜨는 불일치가 생긴다.
    active_rows = fetch_all(
        "SELECT wa.region_code, MIN(sr.note) AS region_name, "
        "  wa.alert_type, wa.alert_level, MIN(wa.start_time) AS since "
        "FROM weather_alerts wa "
        "  JOIN station_regions sr ON sr.region_code = wa.region_code "
        "  JOIN stations s ON s.station_code = sr.station_code "
        "WHERE wa.end_time IS NULL AND wa.alert_type IN ('호우','폭염') AND s.line=%(line)s "
        "GROUP BY wa.region_code, wa.alert_type, wa.alert_level",
        {"line": line},
    )
    active = []
    for a in active_rows:
        # 그 구역에 속한 역들의 취약도 상위. station_regions 로 이어야
        # 위 active_rows 와 같은 기준이 된다.
        affected_rows = fetch_all(
            "SELECT s.station_name AS station, MAX(v.avg_delay) AS avg_delay "
            "FROM station_regions sr "
            "  JOIN stations s ON s.station_code = sr.station_code "
            "  LEFT JOIN station_vulnerability v "
            "    ON v.station_code = sr.station_code AND v.alert_type = %(at)s "
            "WHERE sr.region_code = %(rc)s AND s.line = %(line)s "
            "GROUP BY s.station_name "
            "ORDER BY 2 DESC NULLS LAST LIMIT 5",
            {"rc": a["region_code"], "at": a["alert_type"], "line": line},
        )
        affected = [{
            "type": "station", "station": r["station"], "vuln_rank": i + 1,
            "note": f"{a['alert_type']} {a['alert_level']} 시 평균 +{(r['avg_delay'] or 0):.1f}분",
        } for i, r in enumerate(affected_rows)]

        # 영향 '구간'. 역만 내보내면 프론트의 '영향 구간' 카드가 항상 0 이 된다
        # (프론트는 affected 에서 type=="segment" 를 센다).
        # 귀속 규칙: 구간의 두 역 중 하나라도 이 특보구역에 속하면 영향으로 본다.
        #   구간은 두 역에 걸쳐 있어 어느 한쪽만 특보구역이어도 그 선로는 영향을 받는다.
        affected_segments = fetch_all(
            'SELECT sf.station_name AS "from", st.station_name AS "to", '
            "  MAX(v.avg_delay_incr) AS avg_delay_incr "
            "FROM segment_vulnerability v "
            "  JOIN stations sf ON sf.station_code = v.from_station "
            "  JOIN stations st ON st.station_code = v.to_station "
            "WHERE v.line = %(line)s AND v.alert_type = %(at)s "
            "  AND EXISTS ( "
            "    SELECT 1 FROM station_regions sr "
            "     WHERE sr.region_code = %(rc)s "
            "       AND sr.station_code IN (v.from_station, v.to_station) "
            "  ) "
            'GROUP BY sf.station_name, st.station_name '
            "ORDER BY 3 DESC NULLS LAST LIMIT 5",
            {"rc": a["region_code"], "at": a["alert_type"], "line": line},
        )
        affected += [{
            "type": "segment", "from": r["from"], "to": r["to"], "vuln_rank": i + 1,
            "note": f"{a['alert_type']} {a['alert_level']} 시 평균 +{(r['avg_delay_incr'] or 0):.1f}분",
        } for i, r in enumerate(affected_segments)]
        active.append({
            "region_name": a["region_name"], "alert_type": a["alert_type"],
            "alert_level": a["alert_level"],
            # 계약 §2-1(2): 모든 시각은 KST 로 표기. psycopg 는 TIMESTAMPTZ 를 UTC 로 돌려주므로 변환.
            "since": a["since"].astimezone(KST).isoformat(timespec="seconds") if a["since"] else now,
            "affected": affected,
        })
    return {"line": line, "updated_at": now, "active": active}
