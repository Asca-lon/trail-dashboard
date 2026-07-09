DROP TABLE IF EXISTS segment_vulnerability CASCADE;
DROP TABLE IF EXISTS station_vulnerability CASCADE;
DROP TABLE IF EXISTS weather_alerts CASCADE;
DROP TABLE IF EXISTS train_stops CASCADE;
DROP TABLE IF EXISTS stations CASCADE;

CREATE TABLE stations (
    station_code TEXT PRIMARY KEY,
    station_name TEXT NOT NULL,
    line TEXT NOT NULL,
    seq_on_line INTEGER,
    region_code TEXT,
    region_name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION
);

CREATE TABLE train_stops (
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
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ts_line ON train_stops (line, event_time DESC);
CREATE INDEX idx_ts_train ON train_stops (run_date, train_no, seq);
CREATE UNIQUE INDEX uq_ts ON train_stops (run_date, train_no, station_code, event_time);

CREATE TABLE weather_alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    region_code TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    alert_level TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    UNIQUE (region_code, alert_type, alert_level, start_time)
);

CREATE INDEX idx_alert_region ON weather_alerts (region_code, start_time DESC);

CREATE TABLE station_vulnerability (
    station_code TEXT,
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

CREATE TABLE segment_vulnerability (
    from_station TEXT,
    to_station TEXT,
    line TEXT,
    alert_type TEXT,
    alert_level TEXT,
    avg_delay_incr REAL,
    stop_rate REAL,
    sample_n INTEGER,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (from_station, to_station, alert_type, alert_level)
);
