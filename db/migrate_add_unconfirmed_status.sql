-- db/migrate_add_unconfirmed_status.sql
--
-- 계획시각을 못 찾았을 때 실제시각을 복사해 delay_min=0 으로 저장하던 것을 고친다.
-- 그런 행은 '정시'가 아니라 '계산 불가'다. status='실적미확정', delay_min=NULL 로 둔다.
--
-- 실행:
--   docker compose exec -T db psql -U trail -d trail < db/migrate_add_unconfirmed_status.sql

BEGIN;

ALTER TABLE train_stops DROP CONSTRAINT IF EXISTS train_stops_status_check;
ALTER TABLE train_stops ADD CONSTRAINT train_stops_status_check
    CHECK (status IN ('정상','지연','운행중단','실적미확정'));

-- 계획시각 == 실제시각 인 행 = 계획시각을 못 찾아 실제시각을 복사한 것.
-- (진짜로 초 단위까지 정확히 일치할 확률은 무시할 수 있다.)
UPDATE train_stops
   SET delay_min = NULL,
       planned_arrival = NULL,
       status = '실적미확정'
 WHERE planned_arrival IS NOT NULL
   AND actual_arrival IS NOT NULL
   AND planned_arrival = actual_arrival
   AND status <> '운행중단';

COMMIT;

SELECT status, count(*) AS 건수,
       count(delay_min) AS 지연계산됨
FROM train_stops GROUP BY status ORDER BY 2 DESC;
