"""
collector/inspect_delay.py — 지연 계산의 기준선이 맞는지 진단.

배경:
  지연 분포가 이상하다 — 6-10분 구간(24.5%)이 1-5분(23%)보다 많다.
  자연스러운 지연이면 0분에서 단조 감소해야 하는데 봉우리가 있다.
  5분 초과가 44% 인데 KTX 실제 정시율은 95% 대라 자릿수가 다르다.

확인할 것:
  1) API 가 plt_arvl_dt(계획 도착시각)를 주는가?
     주면 CSV(4/24 기준 한 벌)보다 그게 정확하다 — 날짜별 실제 계획이니까.
  2) API 계획시각 vs CSV 계획시각이 얼마나 다른가?
  3) 실제 지연이 어떻게 분포하는가?

실행:
  docker compose exec api python -u collector/inspect_delay.py
"""
import os
import sys
import requests
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.rail_collector import (
    get_planned_time_from_csv, parse_iso_time, load_target_stations, classify_train_type,
)
from collector.db_writer import get_writer_conn

KEY = os.getenv("PUBLIC_DATA_API_KEY")
URL = os.getenv("KORail_RUN_API_URL", "https://apis.data.go.kr/B551457/run/v2").rstrip('/') \
      + "/travelerTrainRunInfo2"
RUN_YMD = os.getenv("INSPECT_DATE", "20260714")


def main():
    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            targets = load_target_stations(cur)
            cur.execute("SELECT station_code, station_name FROM stations WHERE line='경부선'")
            name_of = {str(r['station_code']): r['station_name'] for r in cur.fetchall()}

    print(f"🎯 대상역 {len(targets)}개 / 조회일 {RUN_YMD}\n", flush=True)

    found = []
    for page in range(1, 21):
        r = requests.get(URL, params={
            "serviceKey": requests.utils.unquote(KEY), "pageNo": str(page),
            "numOfRows": "1000", "runYmd": RUN_YMD, "_type": "json"}, timeout=30)
        body = r.json().get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
        if not items:
            break

        if page == 1:
            print("=" * 72)
            print("1) API 가 주는 필드 (첫 항목)")
            print("=" * 72)
            for k, v in sorted(items[0].items()):
                print(f"   {k:20s} = {v}", flush=True)
            print()

        for it in items:
            cd = str(it.get('stn_cd') or it.get('stnCd') or '').strip()
            if cd not in targets:
                continue
            trn = str(it.get('trn_no') or it.get('trnNo') or '').strip()
            if classify_train_type(trn) != 'KTX':
                continue
            found.append(it)
        if len(found) >= 300:
            break

    print("=" * 72)
    print(f"2) API 계획시각(plt_arvl_dt) vs CSV 계획시각  — 표본 {len(found)}건")
    print("=" * 72)

    stats = Counter()
    samples = []
    for it in found:
        cd = str(it.get('stn_cd') or it.get('stnCd') or '').strip()
        trn = str(it.get('trn_no') or it.get('trnNo') or '').strip()
        stn = name_of.get(cd, cd)

        api_plan = parse_iso_time(RUN_YMD, it.get('plt_arvl_dt') or it.get('pltArvlDt'))
        csv_plan = get_planned_time_from_csv(trn, stn, RUN_YMD)
        actual = parse_iso_time(RUN_YMD, it.get('trn_arvl_dt') or it.get('trnArvlDt'))

        stats['총'] += 1
        if api_plan: stats['API계획 있음'] += 1
        if csv_plan: stats['CSV계획 있음'] += 1
        if actual: stats['실제도착 있음'] += 1

        if api_plan and csv_plan and actual and len(samples) < 15:
            import pandas as pd
            d_api = int((pd.Timestamp(actual) - pd.Timestamp(api_plan)).total_seconds() / 60)
            d_csv = int((pd.Timestamp(actual) - pd.Timestamp(csv_plan)).total_seconds() / 60)
            samples.append((trn, stn, api_plan[11:16], csv_plan[11:16], actual[11:16], d_api, d_csv))

    for k, v in stats.items():
        print(f"   {k:14s}: {v}", flush=True)
    print()

    if samples:
        print(f"   {'열차':>5} {'역':>8} {'API계획':>7} {'CSV계획':>7} {'실제':>6} {'지연(API)':>9} {'지연(CSV)':>9}")
        print("   " + "-" * 62)
        for s in samples:
            mark = "  ← 다름" if s[2] != s[3] else ""
            print(f"   {s[0]:>5} {s[1]:>8} {s[2]:>7} {s[3]:>7} {s[4]:>6} {s[5]:>9} {s[6]:>9}{mark}")
    else:
        print("   ⚠️ API 계획시각(plt_arvl_dt)이 비어 있어 비교 불가 → CSV 를 쓸 수밖에 없음")

    print()
    print("=" * 72)
    print("판단")
    print("=" * 72)
    print("  · 'API계획 있음' 이 0 이면 → API 는 계획시각을 안 준다. CSV 가 유일한 방법.")
    print("  · API계획과 CSV계획이 다르면 → CSV(4/24 한 벌)가 그 날짜와 안 맞는다는 뜻.")
    print("    그 경우 API 계획시각을 우선 쓰도록 rail_collector 를 바꿔야 한다.")


if __name__ == "__main__":
    main()
