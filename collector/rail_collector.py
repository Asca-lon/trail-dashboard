import os
import sys
import argparse
import requests
import traceback
import pandas as pd
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

# =====================================================================
# 1. 계획 시간표(CSV) 로드 및 파싱 로직 추가
# =====================================================================
try:
    plan_csv_path = BASE_DIR / 'collector' / 'gyeongbu_plan_total.csv'
    if plan_csv_path.exists():
        plan_df = pd.read_csv(plan_csv_path)
    else:
        plan_df = pd.read_csv('gyeongbu_plan_total.csv')

    id_vars = ['열차번호', '편성', 'direction']
    station_cols = [c for c in plan_df.columns if c not in id_vars and '비고' not in c]
    
    plan_long = plan_df.melt(id_vars=id_vars, value_vars=station_cols, var_name='stn_nm', value_name='plan_time')
    plan_long = plan_long.dropna(subset=['plan_time'])
    plan_long['열차번호'] = plan_long['열차번호'].astype(str).str.replace('.0', '', regex=False)
except Exception:
    plan_long = None

def get_planned_time_from_csv(trn_no, stn_nm, ymd):
    if plan_long is None:
        return None
    match = plan_long[(plan_long['열차번호'] == str(trn_no)) & (plan_long['stn_nm'] == str(stn_nm))]
    if not match.empty:
        time_str = match.iloc[0]['plan_time']
        return parse_iso_time(ymd, time_str)
    return None
# =====================================================================


def parse_iso_time(ymd, time_val):
    if not time_val:
        return None
    s = str(time_val).strip()
    if not s or s in ['None', 'null', '']:
        return None
    
    if len(s) == 14 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}+09:00"
    if len(s) == 6 and s.isdigit():
        return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]} {s[:2]}:{s[2:4]}:{s[4:6]}+09:00"
        
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
                        break

                    data = response.json()
                    header = data.get('response', {}).get('header', {})
                    if str(header.get('resultCode')) not in ['0', '00']:
                        break

                    body = data.get('response', {}).get('body', {})
                    items = body.get('items', {}).get('item', [])

                    if not items:
                        break

                    if isinstance(items, dict):
                        items = [items]

                    batch_data = []
                    stations_to_insert = set()

                    for item in items:
                        trn_no = item.get('trn_no') or item.get('trnNo')
                        stn_cd = item.get('stn_cd') or item.get('stnCd')
                        stn_nm = item.get('stn_nm') or item.get('stnNm')
                        line_nm = item.get('mrnt_nm') or "경부선"

                        if not trn_no or not stn_cd:
                            continue

                        stn_cd_str = str(stn_cd).strip()
                        stn_nm_str = str(stn_nm).strip()

                        if stn_cd_str == 'station_code' or stn_nm_str == 'station_name':
                            continue

                        stations_to_insert.add((stn_cd_str, stn_nm_str, str(line_nm)))

                        seq_val = int(item.get('trn_run_sn') or item.get('trnRunSn') or 0)

                        actual_arr = parse_iso_time(run_ymd_param, item.get('trn_arvl_dt') or item.get('trnArvlDt'))
                        actual_dpt = parse_iso_time(run_ymd_param, item.get('trn_dptre_dt') or item.get('trnDptreDt'))
                        
                        # =====================================================================
                        # 2. CSV 파일에서 계획 시간 가져오도록 수정
                        # =====================================================================
                        csv_planned_time = get_planned_time_from_csv(trn_no, stn_nm_str, run_ymd_param)
                        
                        if csv_planned_time:
                            planned_arr = csv_planned_time
                            planned_dpt = csv_planned_time
                        else:
                            # CSV에 없으면 기존 API 로직 (또는 실제시간 복사) 사용
                            planned_arr = parse_iso_time(run_ymd_param, item.get('plt_arvl_dt') or item.get('pltArvlDt')) or actual_arr
                            planned_dpt = parse_iso_time(run_ymd_param, item.get('plt_dptre_dt') or item.get('pltDptreDt')) or actual_dpt
                        # =====================================================================

                        event_time = actual_arr or actual_dpt or f"{target_date} 00:00:00+09:00"
                        train_type = classify_train_type(trn_no)

                        delay_min = 0
                        status = "정상"

                        if actual_arr and planned_arr:
                            try:
                                act_dt = datetime.fromisoformat(actual_arr)
                                pln_dt = datetime.fromisoformat(planned_arr)
                                diff_seconds = (act_dt - pln_dt).total_seconds()
                                if diff_seconds > 0:
                                    delay_min = int(diff_seconds / 60)
                                    status = "지연"
                            except ValueError:
                                pass
                        elif actual_dpt and planned_dpt:
                            try:
                                act_dt = datetime.fromisoformat(actual_dpt)
                                pln_dt = datetime.fromisoformat(planned_dpt)
                                diff_seconds = (act_dt - pln_dt).total_seconds()
                                if diff_seconds > 0:
                                    delay_min = int(diff_seconds / 60)
                                    status = "지연"
                            except ValueError:
                                pass

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
                            delay_min,
                            status,
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
                                planned_arrival, actual_arrival, planned_departure, actual_departure, delay_min, status, event_time
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (run_date, train_no, station_code, event_time) DO UPDATE SET
                                planned_arrival = EXCLUDED.planned_arrival,
                                actual_arrival = EXCLUDED.actual_arrival,
                                planned_departure = EXCLUDED.planned_departure,
                                actual_departure = EXCLUDED.actual_departure,
                                delay_min = EXCLUDED.delay_min,
                                status = EXCLUDED.status;
                        """, batch_data)
                        conn.commit()
                        print(f"✅ Page {page_no}: {len(batch_data)}건 적재 완료")

                    total_count = body.get('totalCount', 0)
                    if page_no * num_of_rows >= total_count:
                        break

                    page_no += 1

                except Exception as e:
                    traceback.print_exc()
                    conn.rollback()
                    break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str)
    args = parser.parse_args()
    collect_rail_by_date(args.date)