import os
import sys
import argparse
import requests
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn

PUBLIC_API_KEY = os.getenv("PUBLIC_DATA_API_KEY")
KORAIL_RUN_API_URL = os.getenv("KORail_RUN_API_URL", "https://apis.data.go.kr/B551457/run/v2").rstrip('/')

def parse_iso_time(ymd, time_str):
    if not time_str or len(time_str) < 4:
        return None
    s = time_str.strip()
    return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]} {s[:2]}:{s[2:4]}:00+09:00"

def classify_train_type(train_no):
    if not train_no:
        return "일반"
    num_str = "".join(filter(str.isdigit, str(train_no)))
    if not num_str:
        return "일반"
    val = int(num_str)
    if val < 200:
        return "KTX"
    elif val < 1000:
        return "새마을"
    else:
        return "무궁화"

def collect_rail_by_date(target_date=None):
    if not PUBLIC_API_KEY:
        print("❌ PUBLIC_DATA_API_KEY가 설정되지 않았습니다.")
        return

    if not target_date:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    run_ymd_param = target_date.replace("-", "")
    url = f"{KORAIL_RUN_API_URL}/travelerTrainRunInfo2"
    page_no = 1
    num_of_rows = 1000

    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            while True:
                params = {
                    'serviceKey': requests.utils.unquote(PUBLIC_API_KEY),
                    'pageNo': str(page_no),
                    'numOfRows': str(num_of_rows),
                    'runYmd': run_ymd_param,
                    '_type': 'json'
                }

                try:
                    response = requests.get(url, params=params, timeout=15)
                    if response.status_code != 200:
                        print(f"❌ API 요청 실패: Status {response.status_code}")
                        break

                    data = response.json()
                    header = data.get('response', {}).get('header', {})
                    if str(header.get('resultCode')) not in ['0', '00']:
                        print(f"❌ API 응답 에러: {header}")
                        break

                    body = data.get('response', {}).get('body', {})
                    items = body.get('items', {}).get('item', [])

                    if not items:
                        print("ℹ️ 더 이상 수집할 데이터가 없습니다.")
                        break

                    if isinstance(items, dict):
                        items = [items]

                    batch_data = []
                    stations_to_insert = set()

                    for item in items:
                        trn_no = item.get('trnNo') or item.get('trn_no')
                        stn_cd = item.get('stnCd') or item.get('stn_cd')
                        stn_nm = item.get('stnNm') or item.get('stn_nm') or f"역_{stn_cd}"

                        if not trn_no or not stn_cd:
                            continue

                        stn_cd_str = str(stn_cd)
                        stations_to_insert.add((stn_cd_str, str(stn_nm), "경부선"))

                        seq_val = int(item.get('trnRunSn') or 0)
                        planned_arr = parse_iso_time(run_ymd_param, item.get('arvlTm') or item.get('plan_arvl_tm'))
                        actual_arr = parse_iso_time(run_ymd_param, item.get('trnArvlDt') or item.get('actual_arvl_tm'))
                        planned_dpt = parse_iso_time(run_ymd_param, item.get('dptreTm') or item.get('plan_dpt_tm'))
                        actual_dpt = parse_iso_time(run_ymd_param, item.get('trnDptreDt') or item.get('actual_dpt_tm'))

                        event_time = planned_arr or actual_arr or planned_dpt or actual_dpt
                        if not event_time:
                            event_time = f"{target_date} 00:00:00+09:00"

                        train_type = classify_train_type(trn_no)

                        batch_data.append((
                            target_date,
                            str(trn_no).lstrip('0'),
                            seq_val,
                            stn_cd_str,
                            "경부선",
                            train_type,
                            planned_arr,
                            actual_arr,
                            planned_dpt,
                            actual_dpt,
                            event_time
                        ))

                    if stations_to_insert:
                        cur.executemany("""
                            INSERT INTO stations (station_code, station_name, line)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (station_code) DO NOTHING;
                        """, list(stations_to_insert))

                    if batch_data:
                        cur.executemany("""
                            INSERT INTO train_stops (
                                run_date, train_no, seq, station_code, line, train_type,
                                planned_arrival, actual_arrival, planned_departure, actual_departure, event_time
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (run_date, train_no, station_code, event_time) DO NOTHING;
                        """, batch_data)
                        conn.commit()
                        print(f"✅ Page {page_no}: {len(batch_data)}건 적재 완료")

                    total_count = body.get('totalCount', 0)
                    if page_no * num_of_rows >= total_count:
                        break

                    page_no += 1

                except Exception as e:
                    print("❌ 오류 상세 내역:")
                    traceback.print_exc()
                    conn.rollback()
                    break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="수집할 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()
    
    collect_rail_by_date(args.date)