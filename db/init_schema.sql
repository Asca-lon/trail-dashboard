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
