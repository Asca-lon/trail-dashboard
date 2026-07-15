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
    status TEXT NOT NULL DEFAULT '정상' CHECK (status IN ('정상','지연','운행중단')),
    event_time TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_train_stops UNIQUE (run_date, train_no, station_code, event_time)
);

CREATE INDEX IF NOT EXISTS idx_ts_line ON train_stops (line, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_ts_train ON train_stops (run_date, train_no, seq);

CREATE TABLE IF NOT EXISTS weather_alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    region_code TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    alert_level TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    CONSTRAINT uq_weather_alerts UNIQUE (region_code, alert_type, alert_level, start_time)
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
    avg_delay_incr REAL,
    stop_rate REAL,
    sample_n INTEGER,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (from_station, to_station, alert_type, alert_level)
);
