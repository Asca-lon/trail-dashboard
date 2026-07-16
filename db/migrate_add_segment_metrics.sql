-- db/migrate_add_segment_metrics.sql
--
-- segment_vulnerability 에 avg_delay(절대 지연), delay_rate(지연 비율)를 추가한다.
-- 없으면 구간 상세 화면의 '평균 지연 시간'·'운행 지연률' 카드가 빈다
-- (API 가 avg_delay 를 null 로 내보내고 delay_rate 는 아예 없었다).
--
-- 실행:
--   docker compose exec -T db psql -U trail -d trail < db/migrate_add_segment_metrics.sql
--   그 뒤 반드시 재집계: docker compose exec api python -u processor/vulnerability.py

ALTER TABLE segment_vulnerability ADD COLUMN IF NOT EXISTS avg_delay REAL;
ALTER TABLE segment_vulnerability ADD COLUMN IF NOT EXISTS delay_rate REAL;

\d segment_vulnerability
