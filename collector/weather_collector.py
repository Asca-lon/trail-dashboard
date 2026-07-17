"""
collector/weather_collector.py — 기상 특보 수집 (현재 + 과거 이력 백필)

사용:
  python collector/weather_collector.py                # 현재 발효분
  python collector/weather_collector.py --backfill 90  # 최근 90일 이력 (1회 호출)
  python collector/weather_collector.py --from 20260416 --to 20260715

── 응답 형식 (wrn_met_data.php, help=1 로 확인) ──────────────────
  #  TM_FC,  TM_EF,  TM_IN, STN,  REG_ID, WRN, LVL, CMD, GRD, CNT, RPT
  idx   0       1       2     3      4      5    6    7    8    9   10

  TM_FC : 발표시각 / TM_EF : 발효시각 / REG_ID : 특보구역코드
  WRN   : 특보종류 (문자!)
  LVL   : 1 예비, 2 주의보, 3 경보, 4 중대경보(폭염만)
  CMD   : 1 발표, 2 대치, 3 해제, 4 대치해제(자동), 5 연장, 6 변경, 7 변경해제

⚠️ 종전 코드는 `wrn_cd = cols[6]` 으로 WRN 이 아니라 **LVL** 을 읽고 있었다.
   게다가 WRN 을 숫자로 가정해, LVL=2 인 모든 특보(풍랑·강풍·건조 등)가
   '호우 주의보' 로 둔갑해 저장됐다. 아래에서 바로잡는다.
"""
import os
import sys
import time
import argparse
import requests
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn

KMA_API_KEY = os.getenv("KMA_API_KEY")
KMA_WRN_DATA_URL = os.getenv("KMA_WRN_DATA_URL",
                             "https://apihub.kma.go.kr/api/typ01/url/wrn_met_data.php")

# 일시 장애 재시도 (rail_collector 와 같은 정책).
# 90일 백필은 단일 호출이라 502 한 번에 전부 날아간다 → 재시도가 특히 중요.
MAX_RETRIES = 4
RETRY_BACKOFF = 3          # 3, 9, 27, 81초
TRANSIENT_STATUS = {500, 502, 503, 504}

# WRN: 특보종류 문자코드 (기상청 표준).
#   H = 폭염 — 데이터로 확인됨(LVL=4 중대경보는 폭염만 해당하는데 H 에서 관측).
#   R = 호우
# 스코프(CONTRACT §1)가 호우·폭염 2종이라 나머지는 참고용으로만 둔다.
WRN_MAP = {
    'R': '호우',
    'H': '폭염',
    # ── 스코프 밖 (수집하지 않음, 미지코드 로그와 구분하기 위해 명시) ──
    'W': '강풍', 'C': '한파', 'D': '건조', 'O': '해일',
    'V': '풍랑', 'T': '태풍', 'S': '대설', 'Y': '황사',
}
SCOPE = {'호우', '폭염'}

# LVL: 1 예비 → 아직 발효 전이라 제외. 4 중대경보는 경보로 취급(계약은 주의보/경보 2단계).
LVL_MAP = {'2': '주의보', '3': '경보', '4': '경보'}

# CMD: 발효를 여는 명령 / 닫는 명령
CMD_START = {'1', '2', '5', '6'}   # 발표·대치·연장·변경
CMD_END = {'3', '4', '7'}          # 해제·대치해제·변경해제


def parse_kma_time(tm_str):
    """'202607120300' → '2026-07-12 03:00:00+09:00' (KST)"""
    if not tm_str or len(tm_str.strip()) < 12:
        return None
    s = tm_str.strip()
    return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:00+09:00"


def fetch(tmfc1=None, tmfc2=None):
    """특보 원자료를 받는다. tmfc1/tmfc2(발표시각 범위)로 과거 조회가 된다.

    ※ tmef1/tmef2 는 이 API 가 무시한다(검증됨). 반드시 tmfc 를 쓴다.

    90일 백필은 '단일 호출'이라 일시 장애 한 번에 전부 날아간다.
    502/503/504·네트워크 오류는 지수 백오프로 재시도한다.
    """
    params = {'authKey': KMA_API_KEY, 'disp': '0', 'help': '0'}
    if tmfc1:
        params['tmfc1'] = tmfc1
    if tmfc2:
        params['tmfc2'] = tmfc2

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(KMA_WRN_DATA_URL, params=params, timeout=60)
            if r.status_code in TRANSIENT_STATUS:
                wait = RETRY_BACKOFF ** attempt
                print(f"  ⚠️ HTTP {r.status_code} (일시 오류) — {wait}초 후 재시도 "
                      f"{attempt}/{MAX_RETRIES}", flush=True)
                time.sleep(wait)
                last_err = f"HTTP {r.status_code}"
                continue
            r.raise_for_status()
            for enc in ("euc-kr", "utf-8"):
                r.encoding = enc
                if "\ufffd" not in r.text[:300]:
                    break
            return r.text
        except requests.exceptions.RequestException as e:
            wait = RETRY_BACKOFF ** attempt
            last_err = f"{e.__class__.__name__}: {e}"
            print(f"  ⚠️ 네트워크 오류({e.__class__.__name__}) — {wait}초 후 재시도 "
                  f"{attempt}/{MAX_RETRIES}", flush=True)
            time.sleep(wait)

    raise RuntimeError(f"재시도 {MAX_RETRIES}회 소진 — 마지막 오류: {last_err}")


def parse_events(raw):
    """원자료 → 특보 이벤트 목록. 육상(L) + 스코프(호우·폭염)만."""
    events = []
    unknown_wrn = defaultdict(int)
    skipped_marine = 0

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        cols = [c.strip() for c in line.split(',')]
        if len(cols) < 8:
            continue

        tm_ef = cols[1]      # 발효시각 — 특보가 실제로 걸리는 시각
        region_code = cols[4]
        wrn = cols[5]        # ← 특보종류(문자). 종전 코드는 cols[6](LVL)을 읽었다.
        lvl = cols[6]
        cmd = cols[7]

        # 육상 특보구역만. S* 는 해상(부산앞바다 등)이라 철도와 무관하다.
        if not region_code.startswith('L'):
            skipped_marine += 1
            continue

        alert_type = WRN_MAP.get(wrn)
        if alert_type is None:
            unknown_wrn[wrn] += 1      # 조용히 버리지 않고 남긴다
            continue
        if alert_type not in SCOPE:
            continue

        alert_level = LVL_MAP.get(lvl)
        if alert_level is None:        # LVL=1 예비특보 등
            continue

        t = parse_kma_time(tm_ef)
        if not t:
            continue

        events.append({
            'region_code': region_code, 'alert_type': alert_type,
            'alert_level': alert_level, 'tm_ef': t, 'cmd': cmd,
        })

    if unknown_wrn:
        print(f"  ⚠️ 미지의 WRN 코드(무시됨): {dict(unknown_wrn)}", flush=True)
    print(f"  · 해상(S) 제외 {skipped_marine}건, 스코프 내 이벤트 {len(events)}건", flush=True)
    return events


def build_intervals(events):
    """발표/해제 이벤트를 짝지어 발효 구간(start_time, end_time)으로 만든다.

    ⚠️ 핵심: 특보는 **등급이 바뀌며 대치(CMD=2)** 된다.
        호우 주의보 발표 → 호우 경보로 대치 → 다시 주의보로 대치 → 해제
        이때 '경보 종료'는 해제(CMD=3)가 아니라 **주의보로 대치(CMD=2, LVL=2)** 로 온다.

        그래서 (구역, 종류, 등급)으로 묶으면 안 된다. 그러면 대치 이벤트가
        '주의보 시작'으로만 보이고 '경보 종료'로는 안 보여서 경보가 영영 안 닫힌다.
        실측: 경보 11/124 만 닫히고 113 건이 '발효 중'(최장 58일)으로 남았다.
        end_time 이 NULL 이면 집계가 '지금까지 발효 중'으로 보므로,
        그 구역의 모든 열차가 특보 상태로 잡혀 표본이 부풀려진다.

    → (구역, 종류)로 묶고 **현재 열린 등급**을 추적한다.
      다른 등급의 발표가 오면 이전 등급 구간을 그 시각에 닫고 새로 연다.
    """
    grouped = defaultdict(list)
    for e in events:
        grouped[(e['region_code'], e['alert_type'])].append(e)

    intervals = []
    for (region, atype), evs in grouped.items():
        evs.sort(key=lambda x: x['tm_ef'])
        open_level = None      # 지금 열려 있는 등급
        open_at = None         # 그 등급이 시작된 시각

        for e in evs:
            if e['cmd'] in CMD_END:
                if open_level is not None:
                    intervals.append((region, atype, open_level, open_at, e['tm_ef']))
                    open_level, open_at = None, None

            elif e['cmd'] in CMD_START:
                if open_level is None:
                    open_level, open_at = e['alert_level'], e['tm_ef']
                elif e['alert_level'] != open_level:
                    # 등급 대치: 이전 등급을 여기서 닫고 새 등급을 연다.
                    if e['tm_ef'] > open_at:
                        intervals.append((region, atype, open_level, open_at, e['tm_ef']))
                    open_level, open_at = e['alert_level'], e['tm_ef']
                # 같은 등급이면 연장·변경 → 시작시각 유지

        if open_level is not None:
            intervals.append((region, atype, open_level, open_at, None))   # 아직 발효 중
    return intervals


def save(intervals):
    if not intervals:
        print("ℹ️ 저장할 특보 구간이 없습니다.", flush=True)
        return
    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO weather_alerts (region_code, alert_type, alert_level, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (region_code, alert_type, alert_level, start_time)
                DO UPDATE SET end_time = EXCLUDED.end_time;
            """, intervals)
        conn.commit()
    closed = sum(1 for i in intervals if i[4])
    print(f"✅ 특보 구간 {len(intervals)}건 적재 (해제시각 확인 {closed}건, 발효중 {len(intervals)-closed}건)",
          flush=True)


def collect(tmfc1=None, tmfc2=None):
    """성공하면 True, 실패하면 False. 호출자가 종료코드로 옮긴다(리뷰 3.12)."""
    if not KMA_API_KEY:
        print("❌ KMA_API_KEY가 설정되지 않았습니다.")
        return False
    try:
        label = f"{tmfc1}~{tmfc2}" if tmfc1 else "현재 발효분"
        print(f"🌦️ 기상 특보 수집: {label}", flush=True)
        raw = fetch(tmfc1, tmfc2)
        events = parse_events(raw)
        intervals = build_intervals(events)
        save(intervals)
        return True
    except Exception as e:
        print(f"❌ 기상 데이터 수집 중 오류: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", type=int, metavar="DAYS",
                    help="최근 N일 이력을 한 번에 수집 (예: --backfill 90)")
    ap.add_argument("--from", dest="date_from", help="시작일 YYYYMMDD")
    ap.add_argument("--to", dest="date_to", help="종료일 YYYYMMDD")
    args = ap.parse_args()

    if args.backfill:
        start = (datetime.now() - timedelta(days=args.backfill)).strftime("%Y%m%d")
        end = datetime.now().strftime("%Y%m%d")
        ok = collect(f"{start}0000", f"{end}2359")
    elif args.date_from and args.date_to:
        ok = collect(f"{args.date_from}0000", f"{args.date_to}2359")
    else:
        ok = collect()
    sys.exit(0 if ok else 1)
