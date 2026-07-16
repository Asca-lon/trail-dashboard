#!/usr/bin/env bash
#
# scripts/daily_update.sh — 하루 한 번 데이터 갱신 (cron 용)
#
# 순서가 중요하다:
#   1) 열차 실적  → train_stops     (원시)
#   2) 기상 특보  → weather_alerts  (원시)
#   3) 취약도 집계 → station/segment_vulnerability
# 3번은 1·2를 읽어 매칭하므로 반드시 마지막이다. 수집만 하면 화면 값은 안 바뀐다.
#
# 설치:
#   chmod +x scripts/daily_update.sh
#   crontab -e
#   0 5 * * * /root/trail-dashboard/scripts/daily_update.sh
#
#   (05시인 이유: 철도 실적은 1일 지연으로 들어온다. 새벽에 전일자가 확정된 뒤 돌린다.)

set -uo pipefail

# 스크립트 위치 기준으로 프로젝트 루트 이동 — cron 은 작업 디렉터리가 다르다.
cd "$(dirname "$0")/.." || exit 1

# db 서비스는 profiles: ["db"] 로 격리돼 있어 프로파일을 켜야 인식된다.
export COMPOSE_PROFILES=db

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/daily_$(date +%Y%m%d).log"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

log "===== 일일 갱신 시작 ====="

# 컨테이너가 떠 있는지 먼저 확인. 죽어 있으면 exec 가 조용히 실패한다.
if ! docker compose ps --status running --services 2>/dev/null | grep -qx "api"; then
    log "❌ api 컨테이너가 실행 중이 아님 — 기동 시도"
    docker compose up -d >>"$LOG" 2>&1
    sleep 10
fi

fail=0

# ── 1) 열차 실적 (인자 없으면 '어제'를 수집) ──────────────────
log "① 열차 실적 수집"
if docker compose exec -T api python -u collector/rail_collector.py >>"$LOG" 2>&1; then
    log "   ✅ 완료"
else
    log "   ❌ 실패"
    fail=1
fi

# ── 2) 기상 특보 ─────────────────────────────────────────────
# --backfill 2 인 이유: 인자 없이 돌리면 '현재 발효분'만 받아서,
# 밤사이 발효됐다가 해제된 특보를 통째로 놓친다. 2일치를 겹쳐 받아 빈틈을 막는다.
# (ON CONFLICT DO UPDATE 라 중복 수집은 안전하고, end_time 도 갱신된다.)
log "② 기상 특보 수집 (최근 2일 겹침)"
if docker compose exec -T api python -u collector/weather_collector.py --backfill 2 >>"$LOG" 2>&1; then
    log "   ✅ 완료"
else
    log "   ❌ 실패"
    fail=1
fi

# ── 3) 취약도 집계 ───────────────────────────────────────────
# TRUNCATE 후 전체 재계산이라 매번 최신 상태가 된다.
#
# ⚠️ 원시 수집(①②)이 하나라도 실패하면 집계를 건너뛴다(리뷰 3.12).
#    불완전한 원시 데이터로 TRUNCATE + 재집계하면 멀쩡하던 이전 집계를 지우고
#    구멍 난 결과로 덮어쓴다. 옛 집계를 그대로 두는 편이 안전하다.
if [ "$fail" -ne 0 ]; then
    log "③ 취약도 집계 — 건너뜀 (원시 수집 실패. 불완전한 데이터로 덮어쓰지 않음)"
    log "   → 원인 해결 후 수동 실행: docker compose exec api python -u processor/vulnerability.py"
else
    log "③ 취약도 집계 (역 + 구간)"
    if docker compose exec -T api python -u processor/vulnerability.py >>"$LOG" 2>&1; then
        log "   ✅ 완료"
    else
        log "   ❌ 실패"
        fail=1
    fi
fi

# ── 결과 요약 ────────────────────────────────────────────────
log "── 현재 적재 상태 ──"
docker compose exec -T db psql -U trail -d trail -t -A -F' | ' -c "
SELECT 'train_stops', count(*), max(run_date)::text FROM train_stops
UNION ALL SELECT 'weather_alerts', count(*), max(start_time)::text FROM weather_alerts
UNION ALL SELECT 'station_vuln', count(*), max(updated_at)::text FROM station_vulnerability
UNION ALL SELECT 'segment_vuln', count(*), max(updated_at)::text FROM segment_vulnerability;
" 2>>"$LOG" | tee -a "$LOG"

if [ "$fail" -eq 0 ]; then
    log "===== 일일 갱신 완료 ====="
else
    log "===== 일일 갱신 완료 (일부 실패 — 위 로그 확인) ====="
fi

# 30일 지난 로그 정리
find "$LOG_DIR" -name 'daily_*.log' -mtime +30 -delete 2>/dev/null

exit "$fail"
