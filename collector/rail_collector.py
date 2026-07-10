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

def parse_iso_time(ymd, time_val):
    if not time_val:
        return None
    
    s = str(time_val).strip()
    if not s or s in ['None', 'null', '']:
        return None

    if '.' in s:
        s = s.split('.')[0]

    if ':' in s:
        time_part = s.split(' ')[-1] if ' ' in s else s
        return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]} {time_part}+09:00"

    return None

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
                        trn_no = item.get('trn_no') or item.get('trnNo')
                        stn_cd = item.get('stn_cd') or item.get('stnCd')
                        stn_nm = item.get('stn_nm') or item.get('stnNm') or f"역_{stn_cd}"
                        line_nm = item.get('mrnt_nm') or "경부선"

                        if not trn_no or not stn_cd:
                            continue

                        stn_cd_str = str(stn_cd)
                        stations_to_insert.add((stn_cd_str, str(stn_nm), str(line_nm)))

                        seq_val = int(item.get('trn_run_sn') or item.get('trnRunSn') or 0)

                        actual_arr = parse_iso_time(run_ymd_param, item.get('trn_arvl_dt'))
                        actual_dpt = parse_iso_time(run_ymd_param, item.get('trn_dptre_dt'))
                        
                        planned_arr = actual_arr
                        planned_dpt = actual_dpt

                        event_time = actual_arr or actual_dpt or f"{target_date} 00:00:00+09:00"

                        train_type = classify_train_type(trn_no)

                        batch_data.append((
                            target_date,
                            str(trn_no).lstrip('0'),
                            seq_val,
                            stn_cd_str,
                            str(line_nm),
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