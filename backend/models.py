"""
models.py — CONTRACT_V5 §5 의 JSON 모양을 그대로 코드로 옮긴 것.

여기가 API 응답 모양의 단일 기준이다.
- mock/*.json, 실제 응답, 이 파일 셋이 항상 같은 키·타입이어야 한다(§5-1).
- 필드 추가는 허용, 삭제·개명은 계약 변경 절차(문서 → mock → 코드 함께 수정).
- 단위 고정: 지연=분(minute), 비율(delay_rate·stop_rate·vuln)=0~1.

주의: JSON 키 "from" 은 파이썬 예약어라 필드명을 from_ 로 두고 alias="from" 을 준다.
FastAPI 는 응답을 by_alias=True 로 직렬화하므로 실제 JSON 에는 "from" 으로 나간다.
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

# 필터 허용값 고정 (§5-1 (4)). 자유 입력 금지.
AlertType = Literal["대설", "호우", "폭염", "강풍", "태풍", "한파"]
AlertLevel = Literal["주의보", "경보"]
TrainType = Literal["all", "KTX", "무궁화", "새마을"]

_ALIAS = ConfigDict(populate_by_name=True)


# ── GET /lines ────────────────────────────────────────────────
class Line(BaseModel):
    line: str
    stations: list[str]

class LinesResponse(BaseModel):
    lines: list[Line]


# ── GET /vulnerability/segments ───────────────────────────────
class Segment(BaseModel):
    model_config = _ALIAS
    from_: str = Field(alias="from")
    to: str
    avg_delay_incr: float
    stop_rate: float
    sample_n: int

class SegmentsResponse(BaseModel):
    line: str
    alert_type: str
    alert_level: str
    segments: list[Segment]


# ── GET /vulnerability/stations ───────────────────────────────
class StationVuln(BaseModel):
    station: str
    avg_delay: float
    delay_rate: float
    stop_rate: float
    delta_delay: float
    sample_n: int

class StationsResponse(BaseModel):
    line: str
    alert_type: str
    alert_level: str
    stations: list[StationVuln]


# ── GET /heatmap ──────────────────────────────────────────────
class HeatmapNode(BaseModel):
    station: str
    lat: float
    lon: float
    vuln: float

class HeatmapEdge(BaseModel):
    model_config = _ALIAS
    from_: str = Field(alias="from")
    to: str
    vuln: float

class HeatmapResponse(BaseModel):
    line: str
    nodes: list[HeatmapNode]
    edges: list[HeatmapEdge]


# ── GET /station/{code} · GET /segment/{from}/{to} (상세) ──────
class ByAlert(BaseModel):
    alert_type: str
    alert_level: str
    avg_delay: float
    sample_n: int

class Case(BaseModel):
    date: str
    alert_type: Optional[str] = None
    delay_min: Optional[int] = None

class StationDetail(BaseModel):
    station: str
    by_alert: list[ByAlert]
    cases: list[Case]

class SegmentDetail(BaseModel):
    model_config = _ALIAS
    from_: str = Field(alias="from")
    to: str
    by_alert: list[ByAlert]
    cases: list[Case]


# ── GET /checklist ────────────────────────────────────────────
class ChecklistItem(BaseModel):
    rank: int
    target: str
    reason: str
    avg_delay_incr: float
    sample_n: int

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
