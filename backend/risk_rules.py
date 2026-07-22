"""
risk_rules.py — 취약도 등급 산정의 단일 기준.

여기가 역·구간 위험등급을 정하는 유일한 곳이다.
- api.py 가 원시 지표(집계 결과)를 넣으면 등급(risk_level)과 신뢰도(confidence)를 돌려준다.
- 프론트엔드는 이 결과를 '표시만' 한다(자체 임계값 계산 금지) — 노선도·순위표·상세가 어긋나지 않도록.

── 부르는 이름: 위험도가 아니라 '취약도' ─────────────────────────
현재 산식에 들어가는 건 (과거 열차 지연 실적 + 과거 기상특보 매칭)뿐이다.
사고·차량고장·선로장애·실시간 통제는 포함하지 않는다. 그래서 '기상특보 이력 기반 취약도'.
기사 기반 최근 사고 보정이 추가되면 그때 '최종 위험도'라 부른다.

── 표본 기준(프로젝트 내부 데이터 품질 기준, 철도 규정 아님) ─────
  0 ~ 9건   : 표본 부족(insufficient) — '관심'과 구분한다. 관심=위험 낮음, 부족=판단 불가.
 10 ~ 29건  : 등급 산정하되 낮은 신뢰도(low) 표시
 30건 이상  : 일반 등급 산정(normal)
"""
from __future__ import annotations
from typing import Literal, Optional

RiskLevel = Literal[
    "interest",       # 관심 — 위험 낮음
    "warning",        # 주의
    "high",           # 높음
    "insufficient",   # 표본 부족 — 판단 불가
]

# 내부 데이터 품질 기준(철도 운영 규정 아님 → 문서에 그렇게 명시).
MIN_SAMPLE_N = 10        # 이 미만이면 등급 자체를 매기지 않는다(표본 부족).
CONFIDENT_SAMPLE_N = 30  # 이 이상이라야 일반 신뢰도.


def get_confidence(sample_n: int) -> str:
    """표본 수 → 신뢰도 라벨. 등급과 별개로 화면에 함께 표시한다."""
    if sample_n < MIN_SAMPLE_N:
        return "insufficient"
    if sample_n < CONFIDENT_SAMPLE_N:
        return "low"
    return "normal"


def classify_station_risk(
    delta_delay: Optional[float],
    delay_rate: Optional[float],
    sample_n: int,
) -> RiskLevel:
    """역 취약도.

    delta_delay = 특보 시 평균 지연 - 비특보 시 평균 지연 (평시 대비 증가량)
    delay_rate  = 특보 시 5분 이상 지연 비율 (0~1)

    핵심: 평소에도 자주 지연되는 역(높은 delay_rate)과 '기상특보에 취약한' 역
    (평시 대비 크게 늘어난 역)을 구분한다. delta_delay 가 0 이하면 특보 때
    오히려 나아졌다는 뜻이므로 지연율이 높아도 높음으로 올리지 않는다.
    """
    if sample_n < MIN_SAMPLE_N:
        return "insufficient"

    if delta_delay is None or delay_rate is None:
        return "insufficient"

    if delta_delay >= 5:
        return "high"

    if delta_delay >= 2 and delay_rate >= 0.40:
        return "high"

    if delta_delay > 0 and (delta_delay >= 2 or delay_rate >= 0.25):
        return "warning"

    return "interest"


def classify_segment_risk(
    avg_delay_incr: Optional[float],
    sample_n: int,
) -> RiskLevel:
    """구간 취약도.

    avg_delay_incr = 특보 시간대에 이 구간을 통과하며 '새로' 증가한 평균 지연(분).

    5분 = 현재 프로젝트의 KTX 지연 판정 기준과 연결.
    2분 = 내부 조기 점검 기준. 한 번의 지연이 아니라 특보 표본 전체에서 구간 통과 시
          평균 2분 이상 신규 지연이 반복되면 조기 점검 대상으로 본다.
    음수(회복 구간)는 관심으로 분류.
    """
    if sample_n < MIN_SAMPLE_N:
        return "insufficient"

    if avg_delay_incr is None:
        return "insufficient"

    if avg_delay_incr >= 5:
        return "high"

    if avg_delay_incr >= 2:
        return "warning"

    return "interest"


# ── 특보 라벨 ────────────────────────────────────────────────
# 화면에는 '특보'가 아니라 '폭염 경보'처럼 종류와 등급이 나와야 한다.
# 집계 테이블(station/segment_vulnerability)의 PK 가 (…, alert_type, alert_level)이라
# 데이터는 조합별로 있는데, 조회 시 GROUP BY 로 합치면 그 정보가 사라진다.
# 그래서 라벨을 별도로 만들어 사유 문구에 넣는다.

def alert_label(alert_type: Optional[str], alert_level: Optional[str]) -> Optional[str]:
    """('호우','경보') → '호우 경보'. 하나라도 없으면 None(라벨 생략)."""
    # '전체'는 조합을 특정하지 않는다는 뜻이므로 라벨을 만들지 않는다.
    if not alert_type or not alert_level:
        return None
    if alert_type == "전체" or alert_level == "전체":
        return None
    return f"{alert_type} {alert_level}"


def _head(alert: Optional[str], dominant: bool) -> str:
    """사유 문구의 머리말.

    alert 없음      → '특보 시'          (기존 문구 유지)
    특정 조합 조회   → '폭염 경보 시'      (지표가 그 조합의 값이므로 그대로 단정)
    전체 합산 조회   → '폭염 경보 영향 최대 ·'
        ⚠️ 이때 지표는 여러 특보를 합친 가중평균이다. 특정 특보의 값이 아니므로
           '…시'라고 쓰면 그 특보만의 수치로 오독된다. 영향이 가장 큰 특보를
           '지목'만 하고 수치는 구간·역 전체 기준임을 문구로 구분한다.
    """
    if not alert:
        return "특보 시"
    return f"{alert} 영향 최대 ·" if dominant else f"{alert} 시"


# ── 사유(risk_reason) 문구 ────────────────────────────────────
# 등급과 문구가 어긋나지 않도록 여기서 같이 만든다. 프론트는 이 문구를 그대로 표시한다.

def station_risk_reason(
    level: RiskLevel,
    delta_delay: Optional[float],
    delay_rate: Optional[float],
    sample_n: int,
    alert: Optional[str] = None,
    dominant: bool = False,
) -> str:
    # 표본 부족은 특보와 무관한 판정이므로 라벨을 붙이지 않는다.
    if level == "insufficient":
        return f"표본 {sample_n}건으로 판단 근거 부족"
    h = _head(alert, dominant)
    if level == "high":
        if delta_delay is not None and delta_delay >= 5:
            return f"{h} 평시보다 평균 지연이 {delta_delay:.1f}분 증가"
        return f"{h} 지연율 {(delay_rate or 0):.0%}, 평시보다 {delta_delay:.1f}분 증가"
    if level == "warning":
        if delta_delay is not None and delta_delay >= 2:
            return f"{h} 평시보다 평균 지연이 {delta_delay:.1f}분 증가"
        return f"{h} 지연율 {(delay_rate or 0):.0%}"
    return f"{h} 평시 대비 지연 증가가 뚜렷하지 않음"


def segment_risk_reason(
    level: RiskLevel,
    avg_delay_incr: Optional[float],
    sample_n: int,
    alert: Optional[str] = None,
    dominant: bool = False,
) -> str:
    if level == "insufficient":
        return f"표본 {sample_n}건으로 판단 근거 부족"
    h = _head(alert, dominant)
    if level == "high":
        # 기존엔 '5분 이상'이라고만 했다. 화면의 avg_delay_incr 열과 같은 값을
        # 문구에도 보여 주면 사유와 수치가 어긋나 보이지 않는다.
        return f"{h} 구간 평균 신규 지연 {(avg_delay_incr or 0):.1f}분"
    if level == "warning":
        return f"{h} 구간 평균 신규 지연 {(avg_delay_incr or 0):.1f}분"
    return f"{h} 구간 신규 지연이 크지 않음"
