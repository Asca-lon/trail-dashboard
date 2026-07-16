"""
processor/recompute_delay.py — 이미 수집된 train_stops 의 지연을 다시 계산한다.

왜 필요한가:
  계획시각 CSV(gyeongbu_plan_total.csv) 없이 백필하면
  planned_arrival 이 actual_arrival 로 대체되어 delay_min 이 전부 0 이 된다.

  하지만 actual_arrival 은 처음부터 정상 저장돼 있다.
  즉 API 를 다시 부를 필요 없이, DB 안에서 계획시각만 붙여 다시 계산하면 된다.
  (90일 재수집 5시간 → 재계산 수십 초)

실행:
  docker compose exec api python -u processor/recompute_delay.py           # 미리보기
  docker compose exec api python -u processor/recompute_delay.py --apply   # 실제 반영

전제:
  - collector/gyeongbu_plan_total.csv 가 있어야 한다 (없으면 python collector/excel_to_csv.py)
  - train_stops.actual_arrival 이 채워져 있어야 한다
"""
import sys
import argparse
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn
from collector.rail_collector import plan_long, plan_load_error, parse_iso_time


def build_plan_lookup():
    """(열차번호, 역명) → 'HH:MM:SS' 계획시각 딕셔너리."""
    if plan_long is None:
        raise SystemExit(f"❌ 계획시각 CSV 로딩 실패: {plan_load_error}\n"
                         f"   → python collector/excel_to_csv.py 먼저 실행")
    lut = {}
    for r in plan_long.itertuples(index=False):
        key = (str(r.열차번호).strip(), str(r.stn_nm).strip())
        if key not in lut:
            lut[key] = r.plan_time
    return lut


def main(apply=False):
    lut = build_plan_lookup()
    print(f"🗓️ 계획시각 {len(lut):,}쌍 로드", flush=True)

    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.run_date, t.train_no, t.station_code, s.station_name,
                       t.actual_arrival, t.delay_min
                FROM train_stops t
                JOIN stations s ON s.station_code = t.station_code
                WHERE t.actual_arrival IS NOT NULL
            """)
            rows = cur.fetchall()
    print(f"📊 대상 {len(rows):,}행 (actual_arrival 있음)", flush=True)

    updates, unmatched, changed = [], 0, 0
    for r in rows:
        key = (str(r['train_no']).strip(), str(r['station_name']).strip())
        plan_time = lut.get(key)
        if not plan_time:
            unmatched += 1
            continue

        ymd = r['run_date'].strftime('%Y%m%d')
        planned_iso = parse_iso_time(ymd, plan_time)
        if not planned_iso:
            unmatched += 1
            continue

        planned = pd.Timestamp(planned_iso)
        actual = pd.Timestamp(r['actual_arrival'])

        diff_min = int((actual - planned).total_seconds() / 60)

        # 자정을 넘긴 열차: 계획 23:50 / 실제 00:10 이면 -1420분이 된다.
        # 하루(1440분)를 더해 보정. 반대로 큰 양수면 하루를 뺀다.
        if diff_min < -720:
            diff_min += 1440
        elif diff_min > 720:
            diff_min -= 1440

        new_delay = diff_min if diff_min > 0 else 0
        new_status = "지연" if new_delay > 0 else "정상"

        if new_delay != (r['delay_min'] or 0):
            changed += 1
        updates.append((planned_iso, new_delay, new_status,
                        r['run_date'], r['train_no'], r['station_code']))

    print(f"  · 계획시각 매칭 실패 {unmatched:,}행 (시각표에 없는 열차)", flush=True)
    print(f"  · 값이 바뀌는 행 {changed:,} / 갱신 대상 {len(updates):,}", flush=True)

    if updates:
        d = [u[1] for u in updates]
        pos = [x for x in d if x > 0]
        print(f"  · 재계산 결과: 지연>0 {len(pos):,}건, "
              f"평균 {sum(pos)/len(pos):.1f}분, 최대 {max(pos) if pos else 0}분", flush=True)

    if not apply:
        print("\n미리보기입니다. 반영하려면 --apply 를 붙이세요.", flush=True)
        return

    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany("""
                UPDATE train_stops
                   SET planned_arrival = %s, delay_min = %s, status = %s
                 WHERE run_date = %s AND train_no = %s AND station_code = %s
            """, updates)
        conn.commit()
    print(f"✅ {len(updates):,}행 갱신 완료. 이제 집계를 다시 돌리세요:", flush=True)
    print("   python processor/vulnerability.py", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="실제 DB 에 반영")
    main(ap.parse_args().apply)
