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
    """
    params = {'authKey': KMA_API_KEY, 'disp': '0', 'help': '0'}
    if tmfc1:
        params['tmfc1'] = tmfc1
    if tmfc2:
        params['tmfc2'] = tmfc2

    r = requests.get(KMA_WRN_DATA_URL, params=params, timeout=60)
    r.raise_for_status()
    for enc in ("euc-kr", "utf-8"):
        r.encoding = enc
        if "\ufffd" not in r.text[:300]:
            break
    return r.text


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

    같은 (구역, 종류, 등급) 안에서 시간순으로 훑으며
      발표(CMD 1/2/5/6) → 구간 열기
      해제(CMD 3/4/7)  → 구간 닫기
    끝까지 안 닫힌 구간은 end_time=None (아직 발효 중).
    """
    grouped = defaultdict(list)
    for e in events:
        grouped[(e['region_code'], e['alert_type'], e['alert_level'])].append(e)

    intervals = []
    for (region, atype, alevel), evs in grouped.items():
        evs.sort(key=lambda x: x['tm_ef'])
        open_at = None
        for e in evs:
            if e['cmd'] in CMD_START:
                if open_at is None:
                    open_at = e['tm_ef']
                # 이미 열려 있으면(연장·변경) 시작시각 유지
            elif e['cmd'] in CMD_END:
                if open_at is not None:
                    intervals.append((region, atype, alevel, open_at, e['tm_ef']))
                    open_at = None
        if open_at is not None:
            intervals.append((region, atype, alevel, open_at, None))   # 발효 중
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
    if not KMA_API_KEY:
        print("❌ KMA_API_KEY가 설정되지 않았습니다.")
        return
    try:
        label = f"{tmfc1}~{tmfc2}" if tmfc1 else "현재 발효분"
        print(f"🌦️ 기상 특보 수집: {label}", flush=True)
        raw = fetch(tmfc1, tmfc2)
        events = parse_events(raw)
        intervals = build_intervals(events)
        save(intervals)
    except Exception as e:
        print(f"❌ 기상 데이터 수집 중 오류: {e}")
        traceback.print_exc()


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
        collect(f"{start}0000", f"{end}2359")
    elif args.date_from and args.date_to:
        collect(f"{args.date_from}0000", f"{args.date_to}2359")
    else:
        collect()
