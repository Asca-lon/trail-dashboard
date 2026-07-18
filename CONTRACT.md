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

## 4. DB 스키마 (`db/init_schema.sql`)

> 아래는 **실제 `db/init_schema.sql` 전문**이다(요약이 아니라 파일 그대로).
> compose 의 db 서비스가 최초 기동 시 이 파일을 자동 실행한다.

> **TimescaleDB 적용.** 원시 시계열 두 테이블만 하이퍼테이블로 두고,
> 집계 결과·참조 테이블은 일반 테이블로 남긴다.
> 현재 규모(90일 · 8.4만 행)에서 성능 이득은 크지 않다 — 다노선·다열차종·장기 데이터
> 확장을 위한 시계열 구조다.

```sql
-- db/init_schema.sql — 경부고속선 기상 취약구간 대시보드 스키마
--
-- compose 의 db 서비스가 최초 기동 시 이 파일을 자동 실행한다(01_schema.sql).
--
-- ── TimescaleDB ──────────────────────────────────────────────
-- 원시 시계열 두 테이블(train_stops, weather_alerts)만 하이퍼테이블로 둔다.
-- 집계 결과(station/segment_vulnerability)와 참조 테이블(stations, station_regions)은
-- 시계열이 아니라 일반 테이블로 남긴다.
--
-- ⚠️ 하이퍼테이블은 UNIQUE·PK 에 **파티션 컬럼이 반드시 포함**돼야 한다.
--    그래서 파티션 키를 이렇게 골랐다:
--      train_stops    → run_date    (자연키 run_date+train_no+station_code 에 이미 포함)
--      weather_alerts → start_time  (PK 를 자연키로 바꿔 포함시킴. 아래 주석 참고)
--    train_stops 를 event_time 으로 파티션하면 자연키를 다시 설계해야 하므로 쓰지 않는다.
--
-- 현재 규모(90일 · 8.4만 행)에서 성능 이득은 크지 않다. 다노선·다열차종·장기 데이터로
-- 확장할 때를 위한 시계열 구조다.
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS stations (
    station_code TEXT PRIMARY KEY,
    station_name TEXT NOT NULL,
    line TEXT NOT NULL,
    seq_on_line INTEGER,
    region_code TEXT,
    region_name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS train_stops (
    run_date DATE NOT NULL,
    train_no TEXT NOT NULL,
    seq INTEGER,
    station_code TEXT NOT NULL REFERENCES stations(station_code),
    line TEXT,
    train_type TEXT,
    planned_arrival TIMESTAMPTZ,
    actual_arrival TIMESTAMPTZ,
    planned_departure TIMESTAMPTZ,
    actual_departure TIMESTAMPTZ,
    delay_min INTEGER,
    -- 상태 구분:
    --   정상/지연     : 계획·실제 시각이 모두 있어 지연을 계산한 결과
    --   운행중단      : API 가 중단으로 표기
    --   실적미확정    : 계획시각 또는 실제시각이 없어 지연을 계산할 수 없음
    --                  ← 이 경우 delay_min 은 NULL. 0 으로 채우면 '정시'로 오인되어
    --                    평균을 끌어내리고 정시율을 부풀린다(집계는 NULL 을 제외한다).
    status TEXT NOT NULL DEFAULT '정상'
        CHECK (status IN ('정상','지연','운행중단','실적미확정')),
    -- 실제 기상 노출 시각 = COALESCE(실제도착, 실제출발, 계획도착, 계획출발).
    -- 특보 매칭('그 열차가 실제로 그 시각에 그 기상에 노출됐나')과 시간대별 분석의 기준축.
    -- ⚠️ 계획시각이 아니다. 계획 기준 축이 필요하면 planned_arrival 을 직접 쓴다.
    event_time TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- 자연키: 한 열차(train_no)는 하루(run_date)에 한 역(station_code)에 한 번 선다.
    -- ⚠️ event_time 을 키에 넣으면 안 된다. API 가 실제 도착시각을 재조회마다
    --    분 단위로 다르게 주기 때문에, 같은 정차가 매번 새 행이 되어 중복이 쌓인다.
    --    event_time 은 식별자가 아니라 그 정차의 '속성'이다.
    CONSTRAINT uq_train_stops UNIQUE (run_date, train_no, station_code)
);

CREATE INDEX IF NOT EXISTS idx_ts_line ON train_stops (line, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_ts_train ON train_stops (run_date, train_no, seq);

CREATE TABLE IF NOT EXISTS weather_alerts (
    -- ⚠️ PK 를 자연키로 둔다(종전엔 alert_id BIGSERIAL PRIMARY KEY 였다).
    --    하이퍼테이블은 UNIQUE·PK 에 **파티션 컬럼(start_time)이 반드시 포함**돼야 한다.
    --    alert_id 는 start_time 을 안 담아 create_hypertable 이 거부한다.
    --    alert_id 는 코드 어디에서도 참조하지 않아 없애도 안전하고,
    --    ON CONFLICT 가 쓰던 uq_weather_alerts 와 키가 같아 동작도 그대로다.
    region_code TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    alert_level TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    PRIMARY KEY (region_code, alert_type, alert_level, start_time)
);

CREATE INDEX IF NOT EXISTS idx_alert_region ON weather_alerts (region_code, start_time DESC);

-- 역 ↔ 기상 특보구역 매핑 (1:N)
--
-- stations.region_code 한 칸으로는 부족해서 별도 테이블로 둔다. 이유 두 가지:
--
-- (1) 2026-05-31 특보구역 개편
--     청주·김천·경주·대구 등은 이 날짜로 하위권역이 신설됐다(예: 김천 → 김천북부/남부).
--     우리 분석 창(최근 3개월)이 개편일 전후로 갈리므로, 옛 코드와 새 코드를
--     함께 매칭해야 이력이 끊기지 않는다.
--
-- (2) 권역 귀속 불확실
--     역이 '경주동부'인지 '경주서부'인지 행정경계 없이는 단정할 수 없다.
--     해당 시의 모든 하위권역 + 상위(광역시) 코드를 함께 넣어 과소매칭을 막는다.
--     (과대매칭 위험은 있으나, 같은 시 안의 특보라 철도 영향 판단에는 무리가 없다.)
--
-- vulnerability.py 와 /alerts/active 가 이 테이블로 특보를 역에 귀속시킨다.
CREATE TABLE IF NOT EXISTS station_regions (
    station_code TEXT NOT NULL REFERENCES stations(station_code) ON DELETE CASCADE,
    region_code  TEXT NOT NULL,   -- weather_alerts.region_code 와 매칭되는 L형식 특보구역
    note         TEXT,            -- 구역명·비고 (사람이 읽기 위한 것)
    PRIMARY KEY (station_code, region_code)
);
CREATE INDEX IF NOT EXISTS idx_station_regions_region ON station_regions (region_code);

CREATE TABLE IF NOT EXISTS station_vulnerability (
    station_code TEXT REFERENCES stations(station_code),
    alert_type TEXT,
    alert_level TEXT,
    avg_delay REAL,
    delay_rate REAL,
    stop_rate REAL,
    sample_n INTEGER,
    base_avg_delay REAL,
    delta_delay REAL,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (station_code, alert_type, alert_level)
);

CREATE TABLE IF NOT EXISTS segment_vulnerability (
    from_station TEXT REFERENCES stations(station_code),
    to_station TEXT REFERENCES stations(station_code),
    line TEXT,
    alert_type TEXT,
    alert_level TEXT,
    avg_delay_incr REAL,   -- 구간 신규 지연: 도착역 지연 − 출발역 지연 (이 구간에서 '새로' 생긴 지연)
    avg_delay REAL,        -- 도착역의 절대 지연 평균 (앞 구간에서 누적된 것 포함. 신규 지연과 다르다)
    delay_rate REAL,       -- 도착역 지연 비율 (운영 기준 KTX 5분 이상)
    stop_rate REAL,
    sample_n INTEGER,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (from_station, to_station, alert_type, alert_level)
);


-- ── 하이퍼테이블 전환 ─────────────────────────────────────────
-- 반드시 CREATE TABLE 뒤에 온다. 이미 데이터가 있어도 migrate_data 로 옮긴다.
-- if_not_exists 라 재실행해도 안전하다(compose 재기동 시 이 파일이 다시 돌 수 있다).
SELECT create_hypertable('train_stops', by_range('run_date'),
                         if_not_exists => TRUE, migrate_data => TRUE);

SELECT create_hypertable('weather_alerts', by_range('start_time'),
                         if_not_exists => TRUE, migrate_data => TRUE);
```

**핵심 설계 결정 4가지**

1. **하이퍼테이블 파티션 키는 UNIQUE·PK 에 포함돼야 한다.**
   TimescaleDB 의 제약이다. 그래서 파티션 키를 이렇게 골랐다.
   - `train_stops` → `run_date`. 자연키(`run_date+train_no+station_code`)에 이미 있어
     중복 방지 정책을 그대로 유지한다. `event_time` 으로 파티션하면 자연키를 다시 설계해야 한다.
   - `weather_alerts` → `start_time`. 종전 PK 였던 `alert_id`(BIGSERIAL)는 `start_time` 을
     안 담아 `create_hypertable` 이 거부한다. `alert_id` 는 코드 어디서도 참조하지 않으므로
     PK 를 자연키로 바꿨다. `ON CONFLICT` 는 컬럼 기반이라 동작이 그대로다.

2. **`train_stops` 의 자연키에서 `event_time` 을 뺐다.**
   `event_time`(실제 도착시각)은 API 를 재조회할 때마다 분 단위로 달라진다.
   이걸 UNIQUE 키에 넣었더니 같은 정차가 매번 새 행이 되어 `ON CONFLICT` 가 무력화됐고,
   백필을 돌린 횟수만큼 중복이 쌓였다(실측 9.8배). 한 열차는 하루에 한 역에 한 번 선다.

3. **`station_regions` (역 ↔ 특보구역 1:N).**
   `stations.region_code` 한 칸으로는 부족하다.
   (a) 2026-05-31 특보구역 개편으로 옛/새 코드가 3개월 창 안에 공존하고,
   (b) 역이 '경주동부'인지 '경주서부'인지 행정경계 없이는 단정할 수 없다.
   해당 시의 하위권역 + 상위(광역시) 코드를 모두 넣어 과소매칭을 막는다.

4. **`region_code` 는 기상청 '특보구역'(L형식) 이다.**
   `weather_alerts.region_code` 가 `wrn_met_data.php` 의 `REG_ID`(예: `L1030100`)이므로
   `stations`/`station_regions` 도 같은 체계여야 매칭된다.
   예보구역(`11C20401`)·지점번호(`133`)와 혼동하면 집계가 0행이 된다.

## 5. API 계약 (프론트 ↔ 백엔드)

**C는 이 JSON 모양만 보고 화면을 만든다.** B는 이 모양대로만 응답한다.

> 아래 예시는 `mock/*.json` 에서 그대로 뽑은 것이라 **값까지 동일**하다.
> 실제 응답도 같은 `models.py` 를 거치므로 문서·mock·응답 셋이 항상 일치한다.

> **스코프(현행):** 특보는 **호우·폭염 2종**, 등급은 **주의보·경보 2단계**.
> 과거 사례(`cases[]`)·강수량(`rain_mm`)·예보(`forecast`)·강풍·대설은 응답에 **없다**.
> 노선은 **경부고속선(KTX) 10개 역**: 서울·광명·천안아산·오송·대전·김천구미·동대구·경주·울산·부산.

### `GET /lines`
```json
{
  "lines": [
    {
      "line": "경부선",
      "stations": [
        "서울",
        "광명",
        "천안아산",
        "오송",
        "대전",
        "김천구미",
        "동대구",
        "경주",
        "울산",
        "부산"
      ]
    }
  ]
}
```

### `GET /vulnerability/segments?line=경부선&alert_type=호우&alert_level=경보&train_type=all`
```json
{
  "line": "경부선",
  "alert_type": "호우",
  "alert_level": "경보",
  "segments": [
    {
      "segment_id": "daejeon-gimcheon_gumi",
      "from": "대전",
      "to": "김천구미",
      "avg_delay_incr": 14.6,
      "stop_rate": 0.08,
      "sample_n": 37
    },
    {
      "segment_id": "osong-daejeon",
      "from": "오송",
      "to": "대전",
      "avg_delay_incr": 11.3,
      "stop_rate": 0.05,
      "sample_n": 42
    },
    {
      "segment_id": "gwangmyeong-cheonan_asan",
      "from": "광명",
      "to": "천안아산",
      "avg_delay_incr": 9.2,
      "stop_rate": 0.02,
      "sample_n": 51
    },
    {
      "segment_id": "dongdaegu-ulsan",
      "from": "동대구",
      "to": "울산",
      "avg_delay_incr": 7.8,
      "stop_rate": 0.03,
      "sample_n": 28
    },
    {
      "segment_id": "gimcheon_gumi-dongdaegu",
      "from": "김천구미",
      "to": "동대구",
      "avg_delay_incr": 6.1,
      "stop_rate": 0.01,
      "sample_n": 33
    },
    {
      "segment_id": "ulsan-busan",
      "from": "울산",
      "to": "부산",
      "avg_delay_incr": 5.4,
      "stop_rate": 0.0,
      "sample_n": 7
    }
  ]
}
```
> `segment_id` = `{출발역슬러그}-{도착역슬러그}` (예: `daejeon-gimcheon_gumi`). C가 구간 상세 링크(`?segment_id=`)에 쓴다.
> B가 역명에서 결정적으로 생성한다(DB 컬럼 아님).
> ⚠️ `train_type` 필터는 아직 집계에 차원이 없어 무시된다(all 취급).

### `GET /vulnerability/stations?line=경부선&alert_type=폭염&alert_level=경보`
```json
{
  "line": "경부선",
  "alert_type": "폭염",
  "alert_level": "경보",
  "stations": [
    {
      "station_id": "daejeon",
      "station": "대전",
      "avg_delay": 12.7,
      "delay_rate": 0.44,
      "stop_rate": 0.01,
      "delta_delay": 8.9,
      "sample_n": 61,
      "delay_count": 27
    },
    {
      "station_id": "dongdaegu",
      "station": "동대구",
      "avg_delay": 10.2,
      "delay_rate": 0.38,
      "stop_rate": 0.0,
      "delta_delay": 6.5,
      "sample_n": 55,
      "delay_count": 21
    },
    {
      "station_id": "gimcheon_gumi",
      "station": "김천구미",
      "avg_delay": 8.4,
      "delay_rate": 0.29,
      "stop_rate": 0.0,
      "delta_delay": 5.1,
      "sample_n": 40,
      "delay_count": 12
    },
    {
      "station_id": "cheonan_asan",
      "station": "천안아산",
      "avg_delay": 6.1,
      "delay_rate": 0.21,
      "stop_rate": 0.0,
      "delta_delay": 3.3,
      "sample_n": 48,
      "delay_count": 10
    },
    {
      "station_id": "ulsan",
      "station": "울산",
      "avg_delay": 4.8,
      "delay_rate": 0.15,
      "stop_rate": 0.0,
      "delta_delay": 2.0,
      "sample_n": 6,
      "delay_count": 1
    }
  ]
}
```
> `station_id` = 역명 슬러그(예: `김천구미` → `gimcheon_gumi`). C가 역 상세 링크(`?station_id=`)에 쓴다.
> `delay_count` = 특보 시 지연 발생 건수. DB 컬럼이 아니라 `round(sample_n × delay_rate)` 로 유도한다.

### `GET /heatmap?line=경부선&alert_type=호우`
```json
{
  "line": "경부선",
  "nodes": [
    {
      "station": "서울",
      "lat": 37.554,
      "lon": 126.973,
      "vuln": 0.31
    },
    {
      "station": "광명",
      "lat": 37.515,
      "lon": 126.907,
      "vuln": 0.44
    },
    {
      "station": "천안아산",
      "lat": 37.266,
      "lon": 126.999,
      "vuln": 0.52
    },
    {
      "station": "오송",
      "lat": 36.81,
      "lon": 127.147,
      "vuln": 0.6
    },
    {
      "station": "대전",
      "lat": 36.332,
      "lon": 127.434,
      "vuln": 0.82
    },
    {
      "station": "김천구미",
      "lat": 36.129,
      "lon": 128.114,
      "vuln": 0.71
    },
    {
      "station": "동대구",
      "lat": 35.879,
      "lon": 128.628,
      "vuln": 0.66
    },
    {
      "station": "울산",
      "lat": 35.504,
      "lon": 128.746,
      "vuln": 0.48
    },
    {
      "station": "부산",
      "lat": 35.115,
      "lon": 129.041,
      "vuln": 0.37
    }
  ],
  "edges": [
    {
      "from": "서울",
      "to": "광명",
      "vuln": 0.35
    },
    {
      "from": "광명",
      "to": "천안아산",
      "vuln": 0.55
    },
    {
      "from": "천안아산",
      "to": "오송",
      "vuln": 0.58
    },
    {
      "from": "오송",
      "to": "대전",
      "vuln": 0.69
    },
    {
      "from": "대전",
      "to": "김천구미",
      "vuln": 0.78
    },
    {
      "from": "김천구미",
      "to": "동대구",
      "vuln": 0.62
    },
    {
      "from": "동대구",
      "to": "울산",
      "vuln": 0.57
    },
    {
      "from": "울산",
      "to": "부산",
      "vuln": 0.41
    }
  ]
}
```
> `vuln` 이 `null` 이면 **표본 없음**(데이터 없음). `0.0`(가장 덜 취약)과 구분해서 표시할 것.
> `lat`/`lon` 이 `null` 인 역은 지도에서 건너뛴다.

### `GET /station/{station_id}` — 역 상세
`station_id` 는 슬러그(`daejeon`) 또는 역명(`대전`) 둘 다 받는다.
```json
{
  "station_id": "daejeon",
  "station": "대전",
  "by_alert": [
    {
      "alert_type": "호우",
      "alert_level": "경보",
      "avg_delay": 15.2,
      "sample_n": 34
    },
    {
      "alert_type": "폭염",
      "alert_level": "경보",
      "avg_delay": 12.7,
      "sample_n": 61
    },
    {
      "alert_type": "호우",
      "alert_level": "주의보",
      "avg_delay": 8.4,
      "sample_n": 52
    },
    {
      "alert_type": "폭염",
      "alert_level": "주의보",
      "avg_delay": 6.1,
      "sample_n": 70
    }
  ],
  "hourly_delay": [
    {
      "time": "00:00",
      "weekday_delay": 6.8,
      "holiday_delay": 5.4
    },
    {
      "time": "04:00",
      "weekday_delay": 7.6,
      "holiday_delay": 6.1
    },
    {
      "time": "08:00",
      "weekday_delay": 13.2,
      "holiday_delay": 9.8
    },
    {
      "time": "12:00",
      "weekday_delay": 11.7,
      "holiday_delay": 8.6
    },
    {
      "time": "16:00",
      "weekday_delay": 12.7,
      "holiday_delay": 10.4
    },
    {
      "time": "20:00",
      "weekday_delay": 9.4,
      "holiday_delay": 7.8
    },
    {
      "time": "24:00",
      "weekday_delay": 5.9,
      "holiday_delay": 4.7
    }
  ],
  "alert_delay_comparison": [
    {
      "alert_type": "호우",
      "normal_avg_delay": 8.2,
      "alert_avg_delay": 15.2
    },
    {
      "alert_type": "폭염",
      "normal_avg_delay": 7.1,
      "alert_avg_delay": 12.7
    }
  ]
}
```
> `hourly_delay` = 4시간 버킷 7포인트(`00:00`~`24:00`, KST). `holiday_delay` 는 **주말(토·일)** 을 뜻한다(공휴일 달력 없음).
> `alert_delay_comparison` = 평시 vs 경보 때 평균 지연 비교, **호우·폭염 2행 고정**. 표본 없으면 `null`.

### `GET /segments/details?line=경부선` — 구간 상세 (전 구간 번들)
한 노선의 모든 구간 상세를 배열로 준다. C는 `segment_id` 로 원하는 구간을 찾는다.
(구 `GET /segment/{from}/{to}` 대체 — 단건 왕복 대신 번들 1회.)
```json
{
  "line": "경부선",
  "segments": [
    {
      "segment_id": "daejeon-gimcheon_gumi",
      "from": "대전",
      "to": "김천구미",
      "hourly_delay": [
        {
          "time": "00:00",
          "delay_min": 6.4,
          "type": "actual"
        },
        {
          "time": "04:00",
          "delay_min": 7.1,
          "type": "actual"
        },
        {
          "time": "08:00",
          "delay_min": 11.2,
          "type": "actual"
        },
        {
          "time": "12:00",
          "delay_min": 14.6,
          "type": "actual"
        },
        {
          "time": "16:00",
          "delay_min": 13.1,
          "type": "actual"
        },
        {
          "time": "20:00",
          "delay_min": 15.8,
          "type": "actual"
        },
        {
          "time": "24:00",
          "delay_min": 12.9,
          "type": "actual"
        }
      ],
      "delay_increase_trend": [
        {
          "date": "2026-07-01",
          "delay_increase": 5.2
        },
        {
          "date": "2026-07-02",
          "delay_increase": 7.4
        },
        {
          "date": "2026-07-03",
          "delay_increase": 9.8
        },
        {
          "date": "2026-07-04",
          "delay_increase": 8.3
        },
        {
          "date": "2026-07-05",
          "delay_increase": 6.1
        },
        {
          "date": "2026-07-06",
          "delay_increase": 10.7
        },
        {
          "date": "2026-07-07",
          "delay_increase": 14.6
        }
      ],
      "by_alert": [
        {
          "alert_type": "호우",
          "alert_level": "경보",
          "avg_delay": 14.6,
          "delay_increase": 9.8,
          "stop_rate": 0.08,
          "sample_n": 37
        },
        {
          "alert_type": "호우",
          "alert_level": "주의보",
          "avg_delay": 9.1,
          "delay_increase": 5.4,
          "stop_rate": 0.043,
          "sample_n": 44
        },
        {
          "alert_type": "폭염",
          "alert_level": "경보",
          "avg_delay": 7.2,
          "delay_increase": 3.6,
          "stop_rate": 0.025,
          "sample_n": 25
        }
      ]
    },
    {
      "segment_id": "osong-daejeon",
      "from": "오송",
      "to": "대전",
      "hourly_delay": [
        {
          "time": "00:00",
          "delay_min": 4.8,
          "type": "actual"
        },
        {
          "time": "04:00",
          "delay_min": 5.5,
          "type": "actual"
        },
        {
          "time": "08:00",
          "delay_min": 8.4,
          "type": "actual"
        },
        {
          "time": "12:00",
          "delay_min": 11.3,
          "type": "actual"
        },
        {
          "time": "16:00",
          "delay_min": 10.2,
          "type": "actual"
        },
        {
          "time": "20:00",
          "delay_min": 12.4,
          "type": "actual"
        },
        {
          "time": "24:00",
          "delay_min": 9.9,
          "type": "actual"
        }
      ],
      "delay_increase_trend": [
        {
          "date": "2026-07-01",
          "delay_increase": 3.8
        },
        {
          "date": "2026-07-02",
          "delay_increase": 5.1
        },
        {
          "date": "2026-07-03",
          "delay_increase": 6.9
        },
        {
          "date": "2026-07-04",
          "delay_increase": 6.0
        },
        {
          "date": "2026-07-05",
          "delay_increase": 4.7
        },
        {
          "date": "2026-07-06",
          "delay_increase": 8.6
        },
        {
          "date": "2026-07-07",
          "delay_increase": 11.3
        }
      ],
      "by_alert": [
        {
          "alert_type": "호우",
          "alert_level": "경보",
          "avg_delay": 11.3,
          "delay_increase": 7.1,
          "stop_rate": 0.05,
          "sample_n": 42
        },
        {
          "alert_type": "호우",
          "alert_level": "주의보",
          "avg_delay": 7.6,
          "delay_increase": 4.0,
          "stop_rate": 0.031,
          "sample_n": 31
        }
      ]
    },
    {
      "segment_id": "gwangmyeong-cheonan_asan",
      "from": "광명",
      "to": "천안아산",
      "hourly_delay": [
        {
          "time": "00:00",
          "delay_min": 3.9,
          "type": "actual"
        },
        {
          "time": "04:00",
          "delay_min": 4.6,
          "type": "actual"
        },
        {
          "time": "08:00",
          "delay_min": 6.8,
          "type": "actual"
        },
        {
          "time": "12:00",
          "delay_min": 9.2,
          "type": "actual"
        },
        {
          "time": "16:00",
          "delay_min": 8.7,
          "type": "actual"
        },
        {
          "time": "20:00",
          "delay_min": 9.8,
          "type": "actual"
        },
        {
          "time": "24:00",
          "delay_min": 7.6,
          "type": "actual"
        }
      ],
      "delay_increase_trend": [
        {
          "date": "2026-07-01",
          "delay_increase": 3.1
        },
        {
          "date": "2026-07-02",
          "delay_increase": 4.5
        },
        {
          "date": "2026-07-03",
          "delay_increase": 5.9
        },
        {
          "date": "2026-07-04",
          "delay_increase": 4.8
        },
        {
          "date": "2026-07-05",
          "delay_increase": 3.7
        },
        {
          "date": "2026-07-06",
          "delay_increase": 6.9
        },
        {
          "date": "2026-07-07",
          "delay_increase": 9.2
        }
      ],
      "by_alert": [
        {
          "alert_type": "호우",
          "alert_level": "경보",
          "avg_delay": 9.2,
          "delay_increase": 5.6,
          "stop_rate": 0.02,
          "sample_n": 51
        },
        {
          "alert_type": "호우",
          "alert_level": "주의보",
          "avg_delay": 6.4,
          "delay_increase": 3.8,
          "stop_rate": 0.014,
          "sample_n": 39
        },
        {
          "alert_type": "폭염",
          "alert_level": "주의보",
          "avg_delay": 4.7,
          "delay_increase": 2.1,
          "stop_rate": 0.009,
          "sample_n": 22
        }
      ]
    },
    {
      "segment_id": "dongdaegu-ulsan",
      "from": "동대구",
      "to": "울산",
      "hourly_delay": [
        {
          "time": "00:00",
          "delay_min": 3.2,
          "type": "actual"
        },
        {
          "time": "04:00",
          "delay_min": 3.8,
          "type": "actual"
        },
        {
          "time": "08:00",
          "delay_min": 5.7,
          "type": "actual"
        },
        {
          "time": "12:00",
          "delay_min": 7.8,
          "type": "actual"
        },
        {
          "time": "16:00",
          "delay_min": 7.0,
          "type": "actual"
        },
        {
          "time": "20:00",
          "delay_min": 8.5,
          "type": "actual"
        },
        {
          "time": "24:00",
          "delay_min": 6.8,
          "type": "actual"
        }
      ],
      "delay_increase_trend": [
        {
          "date": "2026-07-01",
          "delay_increase": 2.6
        },
        {
          "date": "2026-07-02",
          "delay_increase": 3.7
        },
        {
          "date": "2026-07-03",
          "delay_increase": 5.1
        },
        {
          "date": "2026-07-04",
          "delay_increase": 4.3
        },
        {
          "date": "2026-07-05",
          "delay_increase": 3.2
        },
        {
          "date": "2026-07-06",
          "delay_increase": 5.9
        },
        {
          "date": "2026-07-07",
          "delay_increase": 7.8
        }
      ],
      "by_alert": [
        {
          "alert_type": "호우",
          "alert_level": "경보",
          "avg_delay": 7.8,
          "delay_increase": 4.7,
          "stop_rate": 0.03,
          "sample_n": 28
        },
        {
          "alert_type": "폭염",
          "alert_level": "주의보",
          "avg_delay": 4.4,
          "delay_increase": 1.9,
          "stop_rate": 0.012,
          "sample_n": 17
        }
      ]
    },
    {
      "segment_id": "gimcheon_gumi-dongdaegu",
      "from": "김천구미",
      "to": "동대구",
      "hourly_delay": [
        {
          "time": "00:00",
          "delay_min": 2.8,
          "type": "actual"
        },
        {
          "time": "04:00",
          "delay_min": 3.1,
          "type": "actual"
        },
        {
          "time": "08:00",
          "delay_min": 4.4,
          "type": "actual"
        },
        {
          "time": "12:00",
          "delay_min": 6.1,
          "type": "actual"
        },
        {
          "time": "16:00",
          "delay_min": 5.9,
          "type": "actual"
        },
        {
          "time": "20:00",
          "delay_min": 6.8,
          "type": "actual"
        },
        {
          "time": "24:00",
          "delay_min": 5.6,
          "type": "actual"
        }
      ],
      "delay_increase_trend": [
        {
          "date": "2026-07-01",
          "delay_increase": 2.1
        },
        {
          "date": "2026-07-02",
          "delay_increase": 2.9
        },
        {
          "date": "2026-07-03",
          "delay_increase": 4.0
        },
        {
          "date": "2026-07-04",
          "delay_increase": 3.5
        },
        {
          "date": "2026-07-05",
          "delay_increase": 2.7
        },
        {
          "date": "2026-07-06",
          "delay_increase": 4.6
        },
        {
          "date": "2026-07-07",
          "delay_increase": 6.1
        }
      ],
      "by_alert": [
        {
          "alert_type": "호우",
          "alert_level": "경보",
          "avg_delay": 6.1,
          "delay_increase": 3.5,
          "stop_rate": 0.01,
          "sample_n": 33
        },
        {
          "alert_type": "호우",
          "alert_level": "주의보",
          "avg_delay": 4.8,
          "delay_increase": 2.4,
          "stop_rate": 0.008,
          "sample_n": 26
        },
        {
          "alert_type": "폭염",
          "alert_level": "주의보",
          "avg_delay": 4.1,
          "delay_increase": 1.6,
          "stop_rate": 0.006,
          "sample_n": 21
        }
      ]
    },
    {
      "segment_id": "ulsan-busan",
      "from": "울산",
      "to": "부산",
      "hourly_delay": [
        {
          "time": "00:00",
          "delay_min": 2.0,
          "type": "actual"
        },
        {
          "time": "04:00",
          "delay_min": 2.4,
          "type": "actual"
        },
        {
          "time": "08:00",
          "delay_min": 3.6,
          "type": "actual"
        },
        {
          "time": "12:00",
          "delay_min": 5.4,
          "type": "actual"
        },
        {
          "time": "16:00",
          "delay_min": 5.1,
          "type": "actual"
        },
        {
          "time": "20:00",
          "delay_min": 5.9,
          "type": "actual"
        },
        {
          "time": "24:00",
          "delay_min": 4.8,
          "type": "actual"
        }
      ],
      "delay_increase_trend": [
        {
          "date": "2026-07-01",
          "delay_increase": 1.4
        },
        {
          "date": "2026-07-02",
          "delay_increase": 2.2
        },
        {
          "date": "2026-07-03",
          "delay_increase": 3.3
        },
        {
          "date": "2026-07-04",
          "delay_increase": 2.8
        },
        {
          "date": "2026-07-05",
          "delay_increase": 2.0
        },
        {
          "date": "2026-07-06",
          "delay_increase": 3.9
        },
        {
          "date": "2026-07-07",
          "delay_increase": 5.4
        }
      ],
      "by_alert": [
        {
          "alert_type": "호우",
          "alert_level": "경보",
          "avg_delay": 5.4,
          "delay_increase": 2.9,
          "stop_rate": 0.0,
          "sample_n": 7
        },
        {
          "alert_type": "호우",
          "alert_level": "주의보",
          "avg_delay": 3.9,
          "delay_increase": 1.7,
          "stop_rate": 0.0,
          "sample_n": 13
        }
      ]
    }
  ]
}
```
> `hourly_delay[].type` 은 항상 `"actual"`(실적). 예보는 만들지 않는다(§1 "유지되는 선").
> `by_alert[].avg_delay` 는 `segment_vulnerability` 에 컬럼 추가 전까지 `null` 가능. 키는 항상 존재.
> `delay_increase` = 구간 신규 지연(`avg_delay_incr`).

### `GET /checklist?line=경부선` — 우선 점검 대상 Top-N
```json
{
  "line": "경부선",
  "items": [
    {
      "rank": 1,
      "target_type": "segment",
      "segment_id": "daejeon-gimcheon_gumi",
      "target": "대전→김천구미 구간",
      "reason": "호우 경보 시 평균 +14.6분",
      "avg_delay_incr": 14.6,
      "sample_n": 37
    },
    {
      "rank": 2,
      "target_type": "segment",
      "segment_id": "osong-daejeon",
      "target": "오송→대전 구간",
      "reason": "호우 경보 시 평균 +11.3분",
      "avg_delay_incr": 11.3,
      "sample_n": 42
    },
    {
      "rank": 3,
      "target_type": "station",
      "station_id": "daejeon",
      "target": "대전역",
      "reason": "폭염 경보 시 지연율 44%",
      "avg_delay_incr": 8.9,
      "sample_n": 61
    },
    {
      "rank": 4,
      "target_type": "segment",
      "segment_id": "gwangmyeong-오송아산",
      "target": "광명→오송아산 구간",
      "reason": "호우 경보 시 평균 +9.2분",
      "avg_delay_incr": 9.2,
      "sample_n": 51
    }
  ]
}
```
> `target_type` = `"station"` | `"segment"`. 그에 따라 `station_id` **또는** `segment_id` 중 하나가 채워진다
> (해당 없는 키는 응답에서 빠진다). C가 상세 페이지 링크에 쓴다.

### `GET /alerts/active?line=경부선` — 현재 발효 특보 + 영향 구간 (실시간)
```json
{
  "line": "경부선",
  "updated_at": "2026-07-07T14:30:00+09:00",
  "active": [
    {
      "region_name": "대전",
      "alert_type": "호우",
      "alert_level": "경보",
      "since": "2026-07-07T13:10:00+09:00",
      "affected": [
        {
          "type": "segment",
          "from": "대전",
          "to": "김천구미",
          "vuln_rank": 1,
          "note": "호우 경보 시 평균 +14.6분"
        },
        {
          "type": "station",
          "station": "대전",
          "vuln_rank": 1,
          "note": "호우 경보 시 지연율 44%"
        }
      ]
    },
    {
      "region_name": "동대구",
      "alert_type": "폭염",
      "alert_level": "주의보",
      "since": "2026-07-07T11:00:00+09:00",
      "affected": [
        {
          "type": "station",
          "station": "동대구",
          "vuln_rank": 2,
          "note": "폭염 경보 시 평균 +10.2분"
        }
      ]
    }
  ]
}
```
> `affected[].type` 이 `station` 이면 `station` 키, `segment` 면 `from`·`to` 키를 쓴다(해당 없는 키는 빠진다).

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
