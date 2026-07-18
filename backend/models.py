"""
models.py — CONTRACT §5 의 JSON 모양을 그대로 코드로 옮긴 것.

여기가 API 응답 모양의 단일 기준이다.
- mock/*.json, 실제 응답, 이 파일 셋이 항상 같은 키·타입이어야 한다(§5-1).
- 필드 추가는 허용, 삭제·개명은 계약 변경 절차(문서 → mock → 코드 함께 수정).
- 단위 고정: 지연=분(minute), 비율(delay_rate·stop_rate·vuln)=0~1.

주의: JSON 키 "from" 은 파이썬 예약어라 필드명을 from_ 로 두고 alias="from" 을 준다.
FastAPI 는 응답을 by_alias=True 로 직렬화하므로 실제 JSON 에는 "from" 으로 나간다.

── 이번 개정(스코프 축소)에서 사라진 것 ──────────────────────
- cases[] (역·구간 공통)      : 과거 사례 표를 화면에서 통째로 제거 → Case 모델 삭제
- rain_mm / current_rain_mm   : 특보 API 는 강수량(mm)을 주지 않는다. 소스 부재
- affected_trains             : cases 에만 있던 필드
- hourly_delay[].type         : 'forecast'(예보) 불가. 실적은 1일 지연(§1 "유지되는 선")
- 강풍 · 대설                 : 특보 종류 스코프는 호우 · 폭염 2종(§1)

── 이번 개정에서 추가된 것 ───────────────────────────────────
- station_id / segment_id / target_type  : C의 상세 페이지 링크용 식별자
- StationDetail.hourly_delay, alert_delay_comparison
- SegmentsDetailsResponse (GET /segments/details) — /segment/{from}/{to} 를 대체
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

# 등급 리터럴은 risk_rules 가 단일 기준. 여기선 응답 필드 타입으로만 재사용한다.
from risk_rules import RiskLevel  # "interest" | "warning" | "high" | "insufficient"

# 필터 허용값 고정 (§5-1 (4)). 자유 입력 금지.
AlertType = Literal["호우", "폭염"]   # 스코프 한정(CONTRACT §1)
AlertLevel = Literal["주의보", "경보"]
TrainType = Literal["all", "KTX", "무궁화", "새마을"]

_ALIAS = ConfigDict(populate_by_name=True)


# ── 식별자(slug) ──────────────────────────────────────────────
# station_id / segment_id 는 C가 상세 페이지 링크(?station_id=…, ?segment_id=…)에 쓴다.
#
# DB 에는 이 슬러그가 없다(stations.station_code 는 코레일 역코드).
# 역명 → 슬러그는 결정적이므로 **B가 여기서 만든다** — A의 스키마를 건드리지 않는다.
# 노선이 늘면 이 표에 행만 추가한다.
STATION_SLUGS: dict[str, str] = {
    "서울": "seoul",
    "광명": "gwangmyeong",
    "천안아산": "cheonan_asan",
    "오송": "osong",
    "대전": "daejeon",
    "김천구미": "gimcheon_gumi",
    "동대구": "dongdaegu",
    "경주": "gyeongju",
    "울산": "ulsan",
    "부산": "busan",
}
SLUG_TO_STATION: dict[str, str] = {v: k for k, v in STATION_SLUGS.items()}


def station_slug(name: str) -> str:
    """역명 → station_id. 표에 없으면 이름을 그대로 쓴다(링크는 살아 있게)."""
    return STATION_SLUGS.get(name, name)


def segment_slug(frm: str, to: str) -> str:
    """(출발역, 도착역) → segment_id.  예: 대전, 김천(구미) → daejeon-gimcheon_gumi"""
    return f"{station_slug(frm)}-{station_slug(to)}"


def resolve_station(station_id: str) -> str:
    """station_id(슬러그) → 역명. 슬러그가 아니면 역명으로 간주해 그대로 돌려준다."""
    return SLUG_TO_STATION.get(station_id, station_id)


# ── GET /lines ────────────────────────────────────────────────
class Line(BaseModel):
    line: str
    stations: list[str]

class LinesResponse(BaseModel):
    lines: list[Line]


# ── GET /vulnerability/segments ───────────────────────────────
class Segment(BaseModel):
    model_config = _ALIAS
    segment_id: str
    from_: str = Field(alias="from")
    to: str
    avg_delay_incr: float
    stop_rate: float
    sample_n: int
    # 등급은 백엔드가 산정한다(risk_rules). 프론트는 표시만. §5-1 필드 추가 허용.
    risk_level: RiskLevel
    confidence: str          # "normal" | "low" | "insufficient" — 표본 신뢰도
    risk_reason: str

class SegmentsResponse(BaseModel):
    line: str
    alert_type: str
    alert_level: str
    segments: list[Segment]


# ── GET /vulnerability/stations ───────────────────────────────
class StationVuln(BaseModel):
    station_id: str
    station: str
    avg_delay: float
    delay_rate: float
    stop_rate: float
    delta_delay: float
    sample_n: int
    # 특보 시 지연 발생 건수. DB 에는 컬럼이 없어 round(sample_n * delay_rate) 로 유도한다
    # (프론트의 추정식과 동일 → 값 일치). 유도 불가 시 null → 프론트가 "약 N건"으로 대체.
    delay_count: Optional[int] = None
    # 등급은 백엔드가 산정한다(risk_rules). 역은 delta_delay + delay_rate 2지표를 함께 본다.
    risk_level: RiskLevel
    confidence: str          # "normal" | "low" | "insufficient" — 표본 신뢰도
    risk_reason: str

class StationsResponse(BaseModel):
    line: str
    alert_type: str
    alert_level: str
    stations: list[StationVuln]


# ── GET /heatmap ──────────────────────────────────────────────
class HeatmapNode(BaseModel):
    station: str
    # stations.lat/lon 은 DDL 상 nullable — 좌표 매핑 전인 역이 있을 수 있다(§4).
    # C는 좌표 없는 노드를 지도에서 건너뛴다.
    lat: Optional[float] = None
    lon: Optional[float] = None
    # null = 해당 특보 표본 없음(데이터 없음). 0.0(가장 덜 취약)과 구분한다.
    # vuln(0~1)은 하위호환용 색상 힌트. 권위 있는 등급은 risk_level 이며 둘은 항상 일치한다.
    vuln: Optional[float] = None
    risk_level: RiskLevel

class HeatmapEdge(BaseModel):
    model_config = _ALIAS
    from_: str = Field(alias="from")
    to: str
    vuln: Optional[float] = None
    risk_level: RiskLevel

class HeatmapResponse(BaseModel):
    line: str
    nodes: list[HeatmapNode]
    edges: list[HeatmapEdge]


# ── GET /station/{station_id} (역 상세) ────────────────────────
class StationByAlert(BaseModel):
    """특보 종류 · 등급별 역 지연 통계. station_vulnerability 그대로."""
    alert_type: str
    alert_level: str
    avg_delay: float
    sample_n: int

class StationHourlyDelay(BaseModel):
    """시간대별 평균 지연. 4시간 버킷, KST 기준.

    holiday_delay 는 **주말(토 · 일)** 을 뜻한다. 공휴일 달력이 없으므로 공휴일은 포함하지 않는다.
    표본이 없는 버킷은 null (§5-1(2): 키는 항상 존재).
    """
    time: str            # "00:00" ~ "24:00"
    weekday_delay: Optional[float] = None
    holiday_delay: Optional[float] = None

class AlertDelayComparison(BaseModel):
    """특보 없을 때 vs 특보(경보) 때 평균 지연 비교. 호우 · 폭염 2행만."""
    alert_type: str
    normal_avg_delay: Optional[float] = None   # station_vulnerability.base_avg_delay
    alert_avg_delay: Optional[float] = None    # station_vulnerability.avg_delay

class StationDetail(BaseModel):
    station_id: str
    station: str
    by_alert: list[StationByAlert]
    hourly_delay: list[StationHourlyDelay]
    alert_delay_comparison: list[AlertDelayComparison]


# ── GET /segments/details (구간 상세 번들) ────────────────────
class SegmentByAlert(BaseModel):
    """특보 종류 · 등급별 구간 통계.

    avg_delay (구간 도착역의 절대 지연 평균) 는 현재 segment_vulnerability 에 **컬럼이 없다.**
    A가 컬럼을 추가하기 전까지 DB 모드에서는 null 로 내려간다(§5-1(2): 키는 항상 존재).
    delay_increase = segment_vulnerability.avg_delay_incr (구간 신규 지연).
    """
    alert_type: str
    alert_level: str
    avg_delay: Optional[float] = None       # 도착역의 절대 지연 평균(누적)
    delay_rate: Optional[float] = None      # 도착역 지연 비율 (운영 기준 KTX 5분 이상)
    delay_increase: float                   # 이 구간에서 '새로' 생긴 지연
    stop_rate: float
    sample_n: int

class SegmentHourlyDelay(BaseModel):
    """시간대별 평균 신규 지연. 4시간 버킷, KST 기준.

    type 은 항상 "actual" — 이 포인트가 실적임을 밝히는 필드다.
    Literal 로 고정했으므로 'forecast' 가 되살아나면 검증에서 막힌다(§1 "유지되는 선").
    """
    time: str
    delay_min: Optional[float] = None
    type: Literal["actual"] = "actual"

class DelayIncreaseTrend(BaseModel):
    """최근 일자별 평균 신규 지연."""
    date: str            # "YYYY-MM-DD"
    delay_increase: Optional[float] = None

class SegmentDetailItem(BaseModel):
    model_config = _ALIAS
    segment_id: str
    from_: str = Field(alias="from")
    to: str
    hourly_delay: list[SegmentHourlyDelay]
    delay_increase_trend: list[DelayIncreaseTrend]
    by_alert: list[SegmentByAlert]

class SegmentsDetailsResponse(BaseModel):
    line: str
    segments: list[SegmentDetailItem]


# ── GET /checklist ────────────────────────────────────────────
class ChecklistItem(BaseModel):
    rank: int
    target_type: Literal["station", "segment"]
    station_id: Optional[str] = None   # target_type == "station" 일 때
    segment_id: Optional[str] = None   # target_type == "segment" 일 때
    target: str
    reason: str
    avg_delay_incr: float
    sample_n: int
    # 점검표 등급도 백엔드가 확정한다(프론트 임계값 제거). 표본 10건 미만은 애초에 목록에서 빠진다.
    risk_level: RiskLevel

class ChecklistResponse(BaseModel):
    line: str
    items: list[ChecklistItem]


# ── GET /alerts/active ────────────────────────────────────────
class Affected(BaseModel):
    model_config = _ALIAS
    type: Literal["segment", "station"]
    from_: Optional[str] = Field(default=None, alias="from")  # segment 일 때
    to: Optional[str] = None                                   # segment 일 때
    station: Optional[str] = None                              # station 일 때
    vuln_rank: Optional[int] = None
    note: str

class ActiveAlert(BaseModel):
    region_name: str
    alert_type: str
    alert_level: str
    since: str
    affected: list[Affected]

class AlertsActiveResponse(BaseModel):
    line: str
    updated_at: str
    active: list[ActiveAlert]


# ── 공통 에러 (§5-1 (3)) ──────────────────────────────────────
class ErrorBody(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorBody
