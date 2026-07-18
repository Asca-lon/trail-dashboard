-- db/migrate_to_timescaledb.sql
--
-- 이미 데이터가 있는 DB 를 하이퍼테이블로 전환한다.
-- (신규 배포는 init_schema.sql 이 알아서 처리하므로 이 파일이 필요 없다.)
--
-- ⚠️ 선행 조건 2가지. 하나라도 빠지면 CREATE EXTENSION 에서 실패한다.
--
-- (1) db 이미지가 timescale/timescaledb 여야 한다 (postgres:16-alpine 이면 확장 자체가 없다).
--
-- (2) 서버가 timescaledb 를 **미리 올린 상태**여야 한다.
--     timescaledb 는 shared_preload_libraries 로 기동 시 로드해야 하는 확장이다.
--     이미지는 최초 initdb 때 postgresql.conf 에 넣어주지만,
--     **기존 볼륨(예: postgres:16-alpine 으로 만든 것)을 쓰면 initdb 를 건너뛰어** 설정이 없다.
--     그러면 이 에러가 난다:
--         FATAL: extension "timescaledb" must be preloaded
--     docker-compose.yml 의 db 서비스에 아래가 있어야 한다(이미 반영돼 있다):
--         command: ["postgres", "-c", "shared_preload_libraries=timescaledb"]
--
--   docker compose down                        # 컨테이너만 내림 (-v 금지! 데이터 유지)
--   docker compose --profile db up -d --build
--   docker compose exec db psql -U trail -d trail -c "SHOW shared_preload_libraries;"
--       → timescaledb 가 보여야 한다
--
-- 실행:
--   docker compose exec -T db psql -U trail -d trail < db/migrate_to_timescaledb.sql

\timing on

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ── weather_alerts: PK 를 자연키로 교체 ──────────────────────
-- 하이퍼테이블은 UNIQUE·PK 에 파티션 컬럼(start_time)을 반드시 포함해야 한다.
-- 기존 PK 는 alert_id(BIGSERIAL) 라 start_time 이 없어 create_hypertable 이 거부한다.
-- alert_id 는 코드 어디서도 참조하지 않으므로 제거해도 안전하다.
BEGIN;
ALTER TABLE weather_alerts DROP CONSTRAINT IF EXISTS weather_alerts_pkey;
ALTER TABLE weather_alerts DROP CONSTRAINT IF EXISTS uq_weather_alerts;
ALTER TABLE weather_alerts DROP COLUMN IF EXISTS alert_id;
ALTER TABLE weather_alerts
    ADD CONSTRAINT weather_alerts_pkey
    PRIMARY KEY (region_code, alert_type, alert_level, start_time);
COMMIT;

-- ── 하이퍼테이블 전환 ─────────────────────────────────────────
-- migrate_data => TRUE : 기존 행을 청크로 옮긴다(테이블이 크면 시간이 걸린다).
-- train_stops 는 run_date 로 파티션한다. 자연키(run_date+train_no+station_code)에
-- 이미 run_date 가 있어 중복 방지 정책을 그대로 유지할 수 있다.
SELECT create_hypertable('train_stops', by_range('run_date'),
                         if_not_exists => TRUE, migrate_data => TRUE);

SELECT create_hypertable('weather_alerts', by_range('start_time'),
                         if_not_exists => TRUE, migrate_data => TRUE);

-- ── 확인 ─────────────────────────────────────────────────────
SELECT hypertable_name, num_chunks
FROM timescaledb_information.hypertables
ORDER BY hypertable_name;

SELECT 'train_stops' AS 테이블, count(*) AS 행수 FROM train_stops
UNION ALL SELECT 'weather_alerts', count(*) FROM weather_alerts;
