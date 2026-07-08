# CONTRACT.md — 기상 취약구간 사전 점검 대시보드 (경부선)

> 팀의 **단일 진실 원천(source of truth)**. DB 스키마와 API JSON 모양을 여기서 확정한다.
> 여기에 합의하면 A·B·C가 서로 안 기다리고 병렬로 개발할 수 있다.
> 변경하려면 **먼저 이 문서를 고치고** 공유한 뒤 코딩한다.

---

## 0. 지금 가장 급한 일 — 백필 (오늘 실행)

철도 API는 **최근 3개월 롤링**이다. **하루 기다릴 때마다 가장 오래된 하루가 영구히 사라진다.**

- [ ] 오늘 즉시 최근 3개월치 **운행계획 + 운행정보**를 백필
- [ ] 같은 기간 **기상 특보**도 백필 (시간대 정렬)
- [ ] 이후 **매일 전일 확정분**을 추가 적재해 3개월 창 유지

> GO/NO-GO 관문은 **통과 완료**: API 호출·인증·실제 도착일시(열차도착일시) 확인됨.

---

## 1. 확정 사실 (설계 전제)

- **대상:** 철도 관리자 — 이상기후 **사전 점검·대비용** (실시간 관제 아님)
- **노선:** 경부선만 구현, **다노선 확장 구조**(노선 코드를 키로)
- **취약도 2층위:** 역 단위 + **역간 구간**(같은 열차 인접 seq A→B의 신규 지연)
- **열차종별 포함:** KTX는 정시율이 높으므로 무궁화·새마을 등 일반열차 포함
- **데이터 범위:** 철도 실적 = 최근 3개월·1일 지연 / 기상 특보 = 철도와 같은 최근 3개월
- **특보 종류 한정:** **호우·폭염만** (주의보+경보). 호우=운행중단 성격, 폭염=지연(서행) 성격
- **실시간 특보 현황 포함:** 과거 이력(취약도 재료)에 더해 **현재 발효 특보**를 폴링 → "취약 구간 + 지금 특보" 결합 경보
- **지연 = 실제도착 − 계획도착**, 시계열 시간축은 **event_time**(예정 도착)
- **조인 키:** (운행일자, 열차번호, 역코드) — 운행계획·운행정보 모두 **역별 여러 행**

> 유지되는 선: **열차 실시간은 불가**(실적 1일 지연). 실시간은 **특보 현황만**.

---

## 1-1. 사용 API 및 처리 흐름

### 사용 API (철도 2 + 기상 3)

| 구분 | API | 용도 |
|---|---|---|
| 철도 | 여객열차 **운행계획** (data.go.kr) | 계획 출발/도착 (예정) |
| 철도 | 여객열차 **운행정보** (data.go.kr) | 실제 출발/도착 (실적, 최근 3개월~1일 전) |
| 기상 | **특보구역 조회** `typ01/url/wrn_reg.php` | 특보구역코드·구역명 → 역↔구역 매핑(1회) |
| 기상 | **특보 발효 이력/현황** `wrn_*` 계열 | 호우·폭염 특보. 기간(tmfc1~tmfc2)=과거 백필, 최신 시각=현재 현황 |

> 특보 발효 이력/현황 API의 정확한 요청주소는 apihub **예특보 → 기상특보** 탭에서 확인(`wrn_*` 계열, 기간 파라미터 지원). 같은 API를 **기간 조회=이력**, **최신 조회=현재 현황**으로 나눠 호출. **호우·폭염만** 필터해서 적재.

### 처리 흐름

```
수집  ① 운행계획 3개월 백필   ② 운행정보 3개월 백필
      ③ 특보 이력 3개월 백필(호우·폭염)   
      ④ [신규] 특보 현재 현황 폴링(30분~1시간)
      + 이후 매일 전일분(①②③) 추가
   ↓
적재(A)  철도→train_stops(원시·event_time) · 특보→weather_alerts · 특보구역→stations.region_code
   ↓
분석(A)  계획×실제 조인→delay_min·status → 특보 시간겹침 결합
        → 역/구간 취약도 집계
        → [신규] 현재 발효 특보 × 취약도 → 실시간 우선점검 경보
   ↓
제공(B)  취약도 순위·히트맵·상세·[신규]현재특보 API  →  화면(C)
```

> 분석(집계)은 **A 소유**, B는 여유 시 보조. B는 집계 결과를 **읽어 API로 노출**만 한다.
> **현재 발효 = weather_alerts.end_time IS NULL.** 별도 테이블 없이 쿼리로 뽑는다(§4 스키마 그대로).

---

## 2. 역할 분담 (1일차 킷 계층 구조 계승)

| 담당 | 소유물 | 주요 작업(현 스코프) |
|---|---|---|
| **A — 데이터·DB·분석** | `db/`, `collector/`, `processor/` | 수집기(운행계획·운행정보·특보), TimescaleDB 스키마·적재, **백필**, 역↔특보구역 매핑, **지연 계산·취약도 집계(분석)** |
| **B — 백엔드·API (통합 관리자 겸)** | `backend/`, **이 계약** | API(취약도 조회·현재 특보·상세), 저장소 통합·병합 조율, **여유 시 A의 분석 보조** |
| **C — 프론트·발표** | `frontend/`, `mock/` | 대시보드(순위표·히트맵·상세), UX, 데모·발표자료 |

> **B가 통합 관리자를 겸한다.** 병합·계약 변경을 B가 조율. 분석(집계)은 A 소유이며 B는 시간이 되면 돕는다.

---

## 2-1. DB ↔ 백엔드 데이터 계약

> 경계선: **A가 수집·적재·분석(지연 계산·취약도 집계)까지 모두 채운다.**
> **B는 A가 만든 결과를 읽어 API로 내보낸다.** (B는 여유 시 A의 분석을 보조)

### (1) 소유권 — 누가 채우나

| 대상 | 채우는 사람 | 비고 |
|---|---|---|
| `stations` 전체 | **A** | 역·특보구역 매핑 포함 |
| `weather_alerts` 전체 | **A** | 특보 원시(이력·현재 현황) |
| `train_stops` 원시 컬럼 | **A** | run_date, train_no, seq, station_code, line, train_type, planned_*, actual_*, **event_time**, ingested_at |
| `train_stops.delay_min`, `train_stops.status` | **A** (분석) | 계획×실제로 계산해 갱신 |
| `station_vulnerability` / `segment_vulnerability` | **A** (분석) | 취약도 집계 산출물 |
| API 응답 | **B** | 위 테이블을 **읽기만** 해서 노출 |

> 즉 B는 DB에 **쓰지 않는다**(읽기 전용). 분석 보조로 참여할 때만 A의 `processor/` 안에서, 결과 스키마를 바꾸지 않고 돕는다.

### (2) A가 지키는 보장 (B가 API로 읽을 때 신뢰해도 되는 것)

- **집계 테이블은 항상 최신**: 매일 배치가 끝나면 station/segment 취약도가 그 시점 기준 완성돼 있다.
- **delay_min·status 는 분석 후 채워져 있다**(원시만 있고 미계산 상태를 B가 읽지 않도록, 아래 순서 준수).
- **event_time 은 절대 NULL 아님** = COALESCE(planned_arrival, actual_arrival).
- **station_code 는 반드시 stations 에 존재**(외래키). 매핑 안 된 역은 stations 먼저 등록.
- **모든 시각은 TIMESTAMPTZ, KST**. 문자열·naive 금지.
- **중복 금지**: 유니크 키 `(run_date, train_no, station_code, event_time)` upsert.
- **seq 는 정차 순서 보존**(구간 조인 `b.seq=a.seq+1` 의존), **train_type 은 정규화**('KTX'/'무궁화'/'새마을').
- **취약도 행에 sample_n 포함**(B·C가 ‘근거 부족’ 판단에 사용).

### (3) NULL·빈 값의 의미 (양쪽 동일 해석)

- 실적 없음(미운행/중단) → `actual_arrival = NULL`. 임의 값·0 금지. A가 이걸 보고 status='운행중단'.
- 특보 발효 중 → `weather_alerts.end_time = NULL`(= B가 ‘현재 발효’로 조회).
- 해당 조건 표본 없음 → 집계 테이블에 행이 없거나 sample_n=0. (B는 이를 API에서 빈 배열로 변환)

### (4) 파이프라인 순서 (A 내부) 와 핸드오프

- **A 내부 순서:** ① 원시 적재 → ② 지연 계산(delay_min·status) → ③ 취약도 집계. 이 순서를 어기면 집계가 빈다.
- **완료 신호:** A는 배치(③까지) 완료를 알린다(상태 테이블 또는 스케줄 순서). **B의 API는 완료된 집계만 읽는다.**
- **백필도 동일 순서**: 원시 백필 전체 → 지연 계산 → 취약도 집계 1회.
- **재적재 시:** A가 특정 날짜를 다시 적재하면 A가 해당 범위 재계산. (upsert 이므로 중복 없음)

### (5) 스키마·결과 변경 규약

- 테이블·집계 컬럼 변경은 **이 문서 먼저 수정 → B(통합 관리자) 공유 → 반영.**
- 집계 테이블(취약도)의 컬럼은 API 응답과 직결되므로, 변경 시 **5장 API 계약도 함께** 갱신.

### (6) B의 분석 보조 규약

- B가 여유 시 도울 때는 A의 `processor/` 안에서 작업하고, **결과 테이블 스키마·의미를 바꾸지 않는다.**
- 보조 결과도 위 (2)의 보장을 동일하게 지킨다. 큰 변경은 A와 합의 후.

### (7) 스키마 변경 안전 가이드 (초보팀 필독)

**원칙: 변경이 "A 내부"에 머물면 자유, "경계(집계 테이블→API→화면)"에 닿으면 계약 절차.**

| 바꾸려는 것 | 안전도 | 규칙 |
|---|---|---|
| 원시 저장 방식 (원시 컬럼 타입, 수집 파싱, 인덱스) | 🟢 자유 | A 내부. 남이 안 봄. 그냥 바꿔도 됨 |
| 지연·취약도 **계산 방식** (로직·중간 단계) | 🟢 자유 | 결과 컬럼·의미가 그대로면 A 내부 |
| 집계 테이블에 **컬럼 추가** | 🟡 대체로 안전 | 추가는 남을 안 깸. 단 B가 쓰려면 알려주기 |
| 집계 테이블 **컬럼 이름·타입 변경/삭제** | 🔴 계약 | B의 조회·API·화면이 연쇄로 깨짐 → 문서+5장 먼저 |
| 필드의 **단위·의미** 변경 (분↔초, 0~1↔0~100) | 🔴 계약 | 타입 안 바뀌어도 조용히 깨짐. 가장 위험 |
| API 응답 JSON 모양 | 🔴 계약 | B↔C 계약(5-1) 절차 그대로 |

**실전 습관 두 가지:**
- **바꾸지 말고 추가하라(뒤로 호환).** 의미를 바꿔야 하면 기존 컬럼을 두고 새 컬럼(예: `delay_sec`)을 더한 뒤 옮겨간다. 삭제·개명은 최후에.
- **스키마를 1주차에 굳혀라.** 워킹 스켈레톤에 실제 데이터를 몇 건 넣어보면 타입 안 맞는 게 그때 드러난다. 그걸 1주차에 겪고 확정하면 2·3주차 경계 변경이 거의 사라진다.

> 헷갈리면 한 문장: **“이 값을 B나 C가 보나?” — 보면 계약, 안 보면 자유.**
---

## 3. 저장소 구조

```
trail-dashboard/
├─ README.md
├─ CONTRACT.md            # 이 문서 = 진실의 원천
├─ docker-compose.yml     # TimescaleDB (+ adminer)
├─ .env.example
├─ db/                    # A
│  ├─ schema.sql          # 아래 4장
│  └─ seed_stations.sql   # 경부선 역·특보구역 매핑
├─ collector/             # A
│  ├─ rail_collector.py     # 운행계획+운행정보 → DB (백필/일배치)
│  ├─ weather_collector.py  # 특보 이력+현재 현황 → DB
│  └─ config.py
├─ processor/             # A (분석)
│  ├─ delay.py            # 계획×실제 조인 → delay_min·status
│  └─ vulnerability.py    # 역/구간 취약도 집계
├─ backend/               # B (읽기 전용 API)
│  ├─ api.py              # FastAPI 엔드포인트
│  ├─ models.py           # pydantic 응답 모델 = 계약을 코드로
│  └─ db.py               # 조회 전용
├─ frontend/              # C
│  └─ (React 또는 HTML/JS: 순위표·지도·상세)
└─ mock/                  # 공유: 병렬 작업의 핵심
   ├─ vulnerability_segments.json
   ├─ vulnerability_stations.json
   ├─ heatmap.json
   └─ alerts_active.json    # 현재 발효 특보(실시간 배너용)
```

> **`mock/` 가 협업의 핵심.** C는 실제 API 없이 mock JSON으로 화면을 완성하고, 나중에 URL만 교체한다.

---

## 4. DB 스키마 (`db/schema.sql`)

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 4-1. 역 + 특보구역 매핑 (참조)
CREATE TABLE stations (
    station_code TEXT PRIMARY KEY,   -- 역코드
    station_name TEXT NOT NULL,
    line         TEXT NOT NULL,      -- '경부선'
    seq_on_line  INTEGER,            -- 노선 내 역 순서(구간 표현용)
    region_code  TEXT,               -- 기상 특보구역코드(수작업 매핑)
    region_name  TEXT,
    lat DOUBLE PRECISION, lon DOUBLE PRECISION
);

-- 4-2. 열차 역별 정차 이벤트 (계획+실제, 핵심 시계열)
CREATE TABLE train_stops (
    run_date          DATE NOT NULL,
    train_no          TEXT NOT NULL,
    seq               INTEGER,          -- 열차운행일련번호(정차 순서) = 구간 생성 키
    station_code      TEXT NOT NULL REFERENCES stations(station_code),
    line              TEXT,
    train_type        TEXT,             -- KTX/무궁화/새마을 (열차번호 규칙으로 분류)
    planned_arrival   TIMESTAMPTZ,
    actual_arrival    TIMESTAMPTZ,
    planned_departure TIMESTAMPTZ,
    actual_departure  TIMESTAMPTZ,
    delay_min         INTEGER,          -- 실제도착 − 계획도착 (분)
    status            TEXT NOT NULL DEFAULT '정상'
                      CHECK (status IN ('정상','지연','운행중단')),
    event_time        TIMESTAMPTZ NOT NULL,  -- COALESCE(planned_arrival, actual_arrival)
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
SELECT create_hypertable('train_stops', 'event_time');
CREATE INDEX idx_ts_line   ON train_stops (line, event_time DESC);
CREATE INDEX idx_ts_train  ON train_stops (run_date, train_no, seq);   -- 구간 조인용
CREATE UNIQUE INDEX uq_ts  ON train_stops (run_date, train_no, station_code, event_time);

-- 4-3. 기상 특보
CREATE TABLE weather_alerts (
    alert_id    BIGSERIAL PRIMARY KEY,
    region_code TEXT NOT NULL,
    alert_type  TEXT NOT NULL,   -- 대설/호우/폭염/강풍/태풍/한파
    alert_level TEXT NOT NULL,   -- 주의보/경보
    start_time  TIMESTAMPTZ NOT NULL,
    end_time    TIMESTAMPTZ
);
CREATE INDEX idx_alert_region ON weather_alerts (region_code, start_time DESC);

-- 4-4. 취약도 집계 (배치로 갱신되는 파생 테이블)
CREATE TABLE station_vulnerability (
    station_code TEXT, alert_type TEXT, alert_level TEXT,
    avg_delay REAL, delay_rate REAL, stop_rate REAL, sample_n INTEGER,
    base_avg_delay REAL, delta_delay REAL, updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (station_code, alert_type, alert_level)
);
CREATE TABLE segment_vulnerability (
    from_station TEXT, to_station TEXT, line TEXT,
    alert_type TEXT, alert_level TEXT,
    avg_delay_incr REAL, stop_rate REAL, sample_n INTEGER,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (from_station, to_station, alert_type, alert_level)
);
```

**구간 신규 지연 계산(참고, processor.py):**
```sql
SELECT a.station_code AS from_st, b.station_code AS to_st,
       b.delay_min - a.delay_min AS delay_incr, b.event_time
FROM train_stops a JOIN train_stops b
  ON a.run_date=b.run_date AND a.train_no=b.train_no AND b.seq = a.seq + 1
WHERE a.delay_min IS NOT NULL AND b.delay_min IS NOT NULL;
```

---

## 5. API 계약 (프론트 ↔ 백엔드)

**C는 이 JSON 모양만 보고 화면을 만든다.** B는 이 모양대로만 응답한다.

> 아래 예시는 `mock/*.json` 과 **바이트 단위로 동일**하다(값 포함). 실제 응답도 같은 models.py 를 거치므로 셋이 항상 일치한다.

### `GET /lines`
```json
{ "lines": [ { "line": "경부선", "stations": ["서울", "영등포", "수원", "천안", "대전", "김천(구미)", "동대구", "밀양", "부산"] } ] }
```

### `GET /vulnerability/segments?line=경부선&alert_type=호우&alert_level=경보&train_type=all`
```json
{
  "line": "경부선", "alert_type": "호우", "alert_level": "경보",
  "segments": [
    { "from": "대전", "to": "김천(구미)", "avg_delay_incr": 14.6, "stop_rate": 0.08, "sample_n": 37 },
    { "from": "천안", "to": "대전", "avg_delay_incr": 11.3, "stop_rate": 0.05, "sample_n": 42 },
    { "from": "영등포", "to": "수원", "avg_delay_incr": 9.2, "stop_rate": 0.02, "sample_n": 51 },
    { "from": "동대구", "to": "밀양", "avg_delay_incr": 7.8, "stop_rate": 0.03, "sample_n": 28 },
    { "from": "김천(구미)", "to": "동대구", "avg_delay_incr": 6.1, "stop_rate": 0.01, "sample_n": 33 },
    { "from": "밀양", "to": "부산", "avg_delay_incr": 5.4, "stop_rate": 0.00, "sample_n": 7 }
  ]
}
```

### `GET /vulnerability/stations?line=경부선&alert_type=폭염&alert_level=경보`
```json
{
  "line": "경부선", "alert_type": "폭염", "alert_level": "경보",
  "stations": [
    { "station": "대전", "avg_delay": 12.7, "delay_rate": 0.44, "stop_rate": 0.01, "delta_delay": 8.9, "sample_n": 61 },
    { "station": "동대구", "avg_delay": 10.2, "delay_rate": 0.38, "stop_rate": 0.00, "delta_delay": 6.5, "sample_n": 55 },
    { "station": "김천(구미)", "avg_delay": 8.4, "delay_rate": 0.29, "stop_rate": 0.00, "delta_delay": 5.1, "sample_n": 40 },
    { "station": "수원", "avg_delay": 6.1, "delay_rate": 0.21, "stop_rate": 0.00, "delta_delay": 3.3, "sample_n": 48 },
    { "station": "밀양", "avg_delay": 4.8, "delay_rate": 0.15, "stop_rate": 0.00, "delta_delay": 2.0, "sample_n": 6 }
  ]
}
```

### `GET /heatmap?line=경부선&alert_type=호우`
```json
{
  "line": "경부선",
  "nodes": [
    { "station": "서울", "lat": 37.554, "lon": 126.973, "vuln": 0.31 },
    { "station": "영등포", "lat": 37.515, "lon": 126.907, "vuln": 0.44 },
    { "station": "수원", "lat": 37.266, "lon": 126.999, "vuln": 0.52 },
    { "station": "천안", "lat": 36.810, "lon": 127.147, "vuln": 0.60 },
    { "station": "대전", "lat": 36.332, "lon": 127.434, "vuln": 0.82 },
    { "station": "김천(구미)", "lat": 36.129, "lon": 128.114, "vuln": 0.71 },
    { "station": "동대구", "lat": 35.879, "lon": 128.628, "vuln": 0.66 },
    { "station": "밀양", "lat": 35.504, "lon": 128.746, "vuln": 0.48 },
    { "station": "부산", "lat": 35.115, "lon": 129.041, "vuln": 0.37 }
  ],
  "edges": [
    { "from": "서울", "to": "영등포", "vuln": 0.35 },
    { "from": "영등포", "to": "수원", "vuln": 0.55 },
    { "from": "수원", "to": "천안", "vuln": 0.58 },
    { "from": "천안", "to": "대전", "vuln": 0.69 },
    { "from": "대전", "to": "김천(구미)", "vuln": 0.78 },
    { "from": "김천(구미)", "to": "동대구", "vuln": 0.62 },
    { "from": "동대구", "to": "밀양", "vuln": 0.57 },
    { "from": "밀양", "to": "부산", "vuln": 0.41 }
  ]
}
```

### `GET /station/{code}` — 역 상세
```json
{
  "station": "대전",
  "by_alert": [
    { "alert_type": "호우", "alert_level": "경보", "avg_delay": 15.2, "sample_n": 34 },
    { "alert_type": "폭염", "alert_level": "경보", "avg_delay": 12.7, "sample_n": 61 },
    { "alert_type": "호우", "alert_level": "주의보", "avg_delay": 8.4, "sample_n": 52 },
    { "alert_type": "폭염", "alert_level": "주의보", "avg_delay": 6.1, "sample_n": 70 }
  ],
  "cases": [
    { "date": "2026-06-28", "alert_type": "호우", "delay_min": 22 },
    { "date": "2026-06-22", "alert_type": "폭염", "delay_min": 15 },
    { "date": "2026-06-15", "alert_type": "호우", "delay_min": 11 },
    { "date": "2026-06-09", "alert_type": null, "delay_min": 7 }
  ]
}
```
> `cases[].alert_type` 는 **null 가능** — 지연 사례가 어느 특보 때문인지 매칭 안 된 경우. C는 null 처리 필요.

### `GET /segment/{from}/{to}` — 구간 상세
```json
{
  "from": "대전", "to": "김천(구미)",
  "by_alert": [
    { "alert_type": "호우", "alert_level": "경보", "avg_delay": 14.6, "sample_n": 37 },
    { "alert_type": "호우", "alert_level": "주의보", "avg_delay": 9.1, "sample_n": 44 },
    { "alert_type": "폭염", "alert_level": "경보", "avg_delay": 7.2, "sample_n": 25 }
  ],
  "cases": [
    { "date": "2026-06-28", "alert_type": "호우", "delay_min": 19 },
    { "date": "2026-06-14", "alert_type": "호우", "delay_min": 12 },
    { "date": "2026-06-03", "alert_type": null, "delay_min": 6 }
  ]
}
```
> 역 상세는 `station`, 구간 상세는 `from`·`to` 로 최상위 키가 다르다. `by_alert`·`cases` 모양은 동일.

### `GET /checklist?line=경부선` — 우선 점검 대상 Top-N
```json
{
  "line": "경부선",
  "items": [
    { "rank": 1, "target": "대전→김천(구미) 구간", "reason": "호우 경보 시 평균 +14.6분", "avg_delay_incr": 14.6, "sample_n": 37 },
    { "rank": 2, "target": "천안→대전 구간", "reason": "호우 경보 시 평균 +11.3분", "avg_delay_incr": 11.3, "sample_n": 42 },
    { "rank": 3, "target": "대전역", "reason": "폭염 경보 시 지연율 44%", "avg_delay_incr": 8.9, "sample_n": 61 },
    { "rank": 4, "target": "영등포→수원 구간", "reason": "호우 경보 시 평균 +9.2분", "avg_delay_incr": 9.2, "sample_n": 51 }
  ]
}
```

### `GET /alerts/active?line=경부선` — 현재 발효 특보 + 영향 구간 (실시간)
현재 발효 중(`end_time IS NULL`)인 호우·폭염 특보와, 그 구역에 걸린 취약 역/구간을 결합.
```json
{
  "line": "경부선",
  "updated_at": "2026-07-07T14:30:00+09:00",
  "active": [
    {
      "region_name": "대전", "alert_type": "호우", "alert_level": "경보",
      "since": "2026-07-07T13:10:00+09:00",
      "affected": [
        { "type": "segment", "from": "대전", "to": "김천(구미)", "vuln_rank": 1, "note": "호우 경보 시 평균 +14.6분" },
        { "type": "station", "station": "대전", "vuln_rank": 1, "note": "호우 경보 시 지연율 44%" }
      ]
    },
    {
      "region_name": "동대구", "alert_type": "폭염", "alert_level": "주의보",
      "since": "2026-07-07T11:00:00+09:00",
      "affected": [
        { "type": "station", "station": "동대구", "vuln_rank": 2, "note": "폭염 경보 시 평균 +10.2분" }
      ]
    }
  ]
}
```
> `affected[]` 는 `type` 에 따라 키가 다르다: `segment` 면 `from`·`to`, `station` 이면 `station`. 해당 없는 키는 응답에서 빠진다(`response_model_exclude_none`).
> 발효 특보가 없으면 `"active": []` (정상). 이 값이 대시보드 상단 배너와 우선 점검 경보의 실시간 소스.
> `/checklist` 는 이 현재 발효분을 반영해 "지금 우선 점검" 항목을 상단에 올린다.

---

## 5-1. 백엔드 ↔ 프론트 계약

> 경계선: **B는 위 JSON 모양대로만 응답**하고, **C는 그 모양만 신뢰**해 화면을 만든다.
> mock 과 실제 응답이 어긋나면 화면이 깨진다 — 이 절이 그걸 막는다.

### (1) mock = 실제 응답의 사본 (동기화 규칙)

- `mock/*.json` 은 5장 예시와 **완전히 같은 키·타입·구조**여야 한다. C는 이걸로 개발.
- **응답 모양을 바꾸려면 B가 (a) 이 문서, (b) mock 파일, (c) 실제 응답을 함께 고치고 공유.** 셋 중 하나만 바꾸면 깨진다.
- 전환은 **URL만 교체**로 끝나야 한다(mock 경로 → 실제 엔드포인트). 파싱 코드 수정이 필요하면 계약이 어긋난 것.

### (2) B가 지키는 응답 보장 (C가 신뢰해도 되는 것)

- **키는 항상 존재**한다. 값이 없으면 키를 빼지 말고 **빈 배열 `[]` / `null`** 로 준다. (C가 `undefined` 방어 안 해도 되게)
- **타입 고정**: 숫자 필드는 숫자(문자열 금지), 목록 필드는 항상 배열.
- **정렬 보장**: 순위(`segments`/`stations`)는 **취약도 높은 순으로 정렬**해 내려준다. C는 그대로 그림.
- **필드 추가는 허용, 삭제·개명은 계약 변경**: B가 필드를 새로 더하는 건 C를 안 깨지만, 지우거나 이름 바꾸면 계약 변경 절차 필요.
- **수치 단위 고정**: 지연은 분(minute), 비율(delay_rate·stop_rate·vuln)은 0~1. C는 표시할 때 % 변환 등 담당.

### (3) 상태 처리 규약 (로딩·에러·빈 데이터)

C는 모든 조회에서 아래 세 상태를 반드시 처리한다. B는 그에 맞는 신호를 준다.

| 상황 | B의 응답 | C의 화면 |
|---|---|---|
| 정상 | 200 + 데이터 | 결과 표시 |
| 데이터 없음(해당 조건 표본 0) | 200 + 빈 배열(`[]`) | “해당 조건 데이터 없음” |
| 근거 부족(`sample_n < 10`) | 데이터에 sample_n 포함 | ‘근거 부족’ 배지 표시 |
| 서버 오류 | 4xx/5xx + `{ "error": { "code", "message" } }` | 오류 메시지 + 재시도 |
| 로딩 중 | — | 로딩 표시(스켈레톤/스피너) |

- 에러 형식은 통일: `{ "error": { "code": "…", "message": "…" } }`
- **빈 데이터는 에러가 아니다.** 표본 0은 200 + `[]` 로, 오류는 4xx/5xx 로 구분.

### (4) 필터 파라미터 규약

- 필터 키·허용값을 고정: `alert_type`(호우/폭염), `alert_level`(주의보/경보), `train_type`(all/KTX/무궁화/새마을), `line`.
- **`all` 또는 파라미터 생략 = 전체**로 동일하게 해석(B·C 합의).
- C가 보내는 값은 이 목록으로 제한(자유 입력 금지). 목록은 `/lines` 등으로 받거나 상수로 공유.

### (5) 데이터 범위 라벨 (표시 의무)

- 응답에 데이터 기준일이 있으면 C는 **‘철도 실적 최근 3개월 기준’** 을 화면에 명시.
- 실적이 과거(1일 지연) 데이터임을 UI에 드러내 “실시간 오해”를 방지.

---

## 6. 취약도 계산 규칙

**지연/상태 판정 (코레일 기준):**
```
if 실적 없음(계획만):          status='운행중단', delay_min=NULL
elif KTX  and delay_min>=5:     status='지연'
elif delay_min>=10:             status='지연'   # 그 외 여객열차
else:                           status='정상'
```

**역 취약도:** (역, 특보종류, 등급)별로 특보 발효 중 정차의
`avg_delay`, `delay_rate`(지연건수/전체), `stop_rate`(중단건수/전체) 집계.
특보 없음(baseline) 대비 `delta_delay = avg_delay − base_avg_delay`.

**구간 취약도:** 인접 seq(A→B) 신규 지연(`delay_incr`)을 특보 발효 구간에서 평균 → `avg_delay_incr`.

**표본 규칙:** `sample_n < 10` 인 항목은 순위에 ‘근거 부족’ 표시(과대해석 방지).

---

## 7. 병렬 작업 규칙

1. **1일차에 4·5장(스키마·API 계약) 확정** → 동시에 시작.
2. C는 `mock/*.json`(5장 예시 그대로)으로 화면 선(先)개발. 실 API는 URL만 교체.
3. **1주차 끝 = 워킹 스켈레톤:** 가짜 데이터라도 수집→DB→집계→API→대시보드 끝단 연결.
4. 매일 15분 공유. 막히면 혼자 하루 붙잡지 말고 페어로.
5. 계약 변경은 코드보다 **이 문서 먼저** 고치고 B가 공유.

---

## 8. 일정

**1주차 — 백필 + 기반 + 워킹 스켈레톤**
- (즉시) A: 3개월 백필 실행 + 특보 백필
- 스키마·계약 확정, C는 mock으로 순위표·지도 레이아웃
- 주말: 가짜 데이터로 끝단 연결 ✅

**2주차 — 실데이터 취약도 + MVP**
- A: 일배치 가동, 역↔구역 매핑 완성, **지연 계산 + 역/구간 취약도 집계** (B가 여유 시 보조)
- B: 집계 결과를 읽는 순위·히트맵·현재특보 API, 통합
- C: 취약도 순위표(역/구간 토글) + 지도 히트맵 + 필터 + 현재 특보 배너
- 역/구간 상세, 특보 종류별 비교, 우선 점검 목록
