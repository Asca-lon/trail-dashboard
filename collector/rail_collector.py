import os
import sys
import time
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

# 일시 장애 재시도 설정.
#   502/503/504 는 공공데이터포털 게이트웨이의 순간 장애로, 잠시 뒤 재시도하면 대개 성공한다.
#   재시도 없이 중단하면 그 날짜가 반쪽만 적재되어 집계가 왜곡된다.
MAX_RETRIES = 4
RETRY_BACKOFF = 3          # 3, 9, 27, 81초
TRANSIENT_STATUS = {500, 502, 503, 504}

# 수집할 열차종류. 경부고속선 프로젝트라 KTX 만. (전체를 받으려면 아래 필터 주석 참고)
TARGET_TRAIN_TYPES = {"KTX"}

# 지연 '판정' 기준(분). 운영 기준을 따른다 — KTX 5분, 일반열차 10분.
# 1분만 늦어도 지연으로 세면 지연율이 실제 운영 기준보다 크게 부풀려진다.
# (delay_min 은 원값 그대로 저장하고, 판정만 이 기준을 쓴다.)
DELAY_THRESHOLD_MIN = {"KTX": 5, "새마을": 10, "무궁화": 10, "일반": 10}
KORAIL_RUN_API_URL = os.getenv("KORail_RUN_API_URL", "https://apis.data.go.kr/B551457/run/v2").rstrip('/')

# =====================================================================
# 1. 계획 시간표(CSV) 로드 및 파싱 로직 추가
# =====================================================================
# 계획시각(시각표) 로딩.
#
# ⚠️ 이 CSV 가 없으면 planned_arr 이 actual_arr 로 대체되어 **지연이 전부 0** 이 된다.
#    (delay_min = actual - planned = 0). 조용히 넘어가면 90일 백필을 다 돌린 뒤
#    집계에서야 발견되므로, 여기서 크게 경고한다.
#    CSV 는 .gitignore 대상(파생물)이라 clone 직후엔 없다:
#        python collector/excel_to_csv.py   ← 반드시 먼저 실행
# =====================================================================
PLAN_CSV_PATH = BASE_DIR / 'collector' / 'gyeongbu_plan_total.csv'
plan_load_error = None
try:
    if not PLAN_CSV_PATH.exists():
        raise FileNotFoundError(f"{PLAN_CSV_PATH} 없음")
    plan_df = pd.read_csv(PLAN_CSV_PATH)

    id_vars = ['열차번호', '편성', 'direction']
    station_cols = [c for c in plan_df.columns if c not in id_vars and '비고' not in c]

    plan_long = plan_df.melt(id_vars=id_vars, value_vars=station_cols, var_name='stn_nm', value_name='plan_time')
    plan_long = plan_long.dropna(subset=['plan_time'])
    plan_long['열차번호'] = plan_long['열차번호'].astype(str).str.replace('.0', '', regex=False)
except Exception as e:
    plan_long = None
    plan_load_error = e

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

def load_target_stations(cur):
    """수집 대상 역 코드 집합을 DB에서 읽는다(= seed_stations.sql 의 경부선 역).

    이 API(travelerTrainRunInfo2)는 runYmd 만 받고 **전국 모든 열차·역**을 돌려준다.
    노선/역 필터 파라미터가 없어 서버 쪽에서 못 줄이므로, 받아온 뒤 여기서 거른다.

    기준을 seed 로 두는 이유:
      - 하드코딩하면 seed_stations.sql 과 어긋난다.
      - region_code 가 있는 역만 취약도 집계에 쓰인다(vulnerability.py 의
        `WHERE region_code IS NOT NULL`). 즉 집계에 쓸 역만 저장하면 충분하다.
    """
    cur.execute(
        "SELECT station_code FROM stations "
        "WHERE line = '경부선' AND region_code IS NOT NULL"
    )
    return {str(r["station_code"]).strip() for r in cur.fetchall()}


def _report_quality(target_date, q):
    """수집 품질 리포트 (리뷰 3.1 — '계획시각 미매칭률 집계').

    계획시각을 못 찾으면 지연을 계산할 수 없다(delay_min=NULL, status='실적미확정').
    그런 행이 많으면 취약도 집계의 표본이 조용히 줄어든다.
    예전에는 실제시각을 복사해 delay=0 으로 저장했는데, 그건 '정시'로 오인되어
    평균을 끌어내렸다. 이제는 제외하지만, **얼마나 제외됐는지는 알아야 한다.**
    """
    total = q['총']
    if not total:
        return
    ok = q['지연계산됨']
    rate = ok / total * 100
    print(f"  📊 {target_date} 품질: 대상 {total:,} / 지연계산 {ok:,} ({rate:.1f}%)", flush=True)
    print(f"     계획시각 출처 — CSV {q['CSV매칭']:,} · API {q['API계획']:,} · 없음 {q['계획없음']:,}", flush=True)
    if q['실제없음'] or q['파싱오류']:
        print(f"     실제시각 없음 {q['실제없음']:,} · 파싱오류 {q['파싱오류']:,}", flush=True)
    if rate < 90:
        print(f"     ⚠️ 지연계산률 {rate:.1f}% — 표본의 {100-rate:.1f}% 가 분석에서 빠집니다.", flush=True)
        if q['계획없음'] > total * 0.1:
            print(f"     → 계획시각 미매칭이 주원인입니다. 시각표 CSV 가 이 날짜와 맞는지 확인하세요"
                  f" (python collector/excel_to_csv.py).", flush=True)


def collect_rail_by_date(target_date=None):
    if not PUBLIC_API_KEY:
        print("❌ PUBLIC_DATA_API_KEY가 설정되지 않았습니다.")
        return False

    if not target_date:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    run_ymd_param = target_date.replace("-", "")
    url = f"{KORAIL_RUN_API_URL}/travelerTrainRunInfo2"
    page_no = 1
    num_of_rows = 1000

    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            # 계획시각이 없으면 지연이 전부 0 으로 저장된다 — 수집하는 의미가 없다.
            # 90일을 다 돌린 뒤 집계에서 발견하는 대신 여기서 멈춘다.
            if plan_long is None:
                print(f"❌ 계획시각 CSV 로딩 실패: {plan_load_error}", flush=True)
                print("   → 이대로 수집하면 planned_arrival 이 actual 로 대체돼 "
                      "지연이 전부 0 이 됩니다.", flush=True)
                print("   → 먼저 실행하세요:  python collector/excel_to_csv.py", flush=True)
                return False
            print(f"🗓️ 계획시각 {len(plan_long):,}건 로드됨", flush=True)

            # 경부선 대상 역만 수집한다(전국 데이터를 다 넣지 않는다).
            target_stations = load_target_stations(cur)
            if not target_stations:
                print("❌ 대상 역이 없습니다. db/seed_stations.sql 이 적재됐는지 확인하세요.")
                return False
            print(f"🎯 수집 대상: 경부선 {len(target_stations)}개 역")

            skipped = 0
            failed = False
            # 데이터 품질 지표 (리뷰 3.1) — 계획시각을 못 찾으면 지연을 계산할 수 없다.
            # 조용히 '실적미확정'으로 빠지면 미매칭률을 알 수 없으므로 여기서 센다.
            q = {'총': 0, 'CSV매칭': 0, 'API계획': 0, '계획없음': 0,
                 '실제없음': 0, '지연계산됨': 0, '파싱오류': 0}
            while True:
                params = {
                    'serviceKey': requests.utils.unquote(PUBLIC_API_KEY),
                    'pageNo': str(page_no),
                    'numOfRows': str(num_of_rows),
                    'runYmd': run_ymd_param,
                    '_type': 'json'
                }

                try:
                    # 502/503/504 와 네트워크 오류는 서버 측 일시 장애다. 여기서 그냥 중단하면
                    # 그 날짜가 '반쪽'만 적재된 채 다음 날짜로 넘어가 데이터에 구멍이 생긴다.
                    # 지수 백오프로 재시도하고, 소진되면 날짜 단위로 실패를 알린다.
                    response = None
                    for attempt in range(1, MAX_RETRIES + 1):
                        try:
                            response = requests.get(url, params=params, timeout=30)
                            if response.status_code in TRANSIENT_STATUS:
                                wait = RETRY_BACKOFF ** attempt
                                print(f"  ⚠️ HTTP {response.status_code} (일시 오류) — "
                                      f"{wait}초 후 재시도 {attempt}/{MAX_RETRIES}", flush=True)
                                time.sleep(wait)
                                response = None
                                continue
                            break
                        except requests.exceptions.RequestException as re_err:
                            wait = RETRY_BACKOFF ** attempt
                            print(f"  ⚠️ 네트워크 오류({re_err.__class__.__name__}) — "
                                  f"{wait}초 후 재시도 {attempt}/{MAX_RETRIES}", flush=True)
                            time.sleep(wait)

                    if response is None:
                        print(f"  ❌ page {page_no}: 재시도 {MAX_RETRIES}회 소진 — "
                              f"{target_date} 미완성 상태로 중단", flush=True)
                        failed = True
                        print(f"     → 나중에 이 날짜만 다시 돌리세요: "
                              f"python collector/rail_collector.py --date {target_date}", flush=True)
                        break

                    if response.status_code != 200:
                        print(f"  ❌ HTTP {response.status_code} — 중단. 응답: {response.text[:300]}", flush=True)
                        failed = True
                        break

                    data = response.json()
                    header = data.get('response', {}).get('header', {})
                    result_code = str(header.get('resultCode'))
                    if result_code not in ['0', '00']:
                        # 쿼터 초과·키 오류 등이 여기로 온다. 조용히 끝내면 원인을 알 수 없다.
                        print(f"  ❌ API 오류 resultCode={result_code}, "
                              f"msg={header.get('resultMsg')} — 중단", flush=True)
                        failed = True
                        break

                    body = data.get('response', {}).get('body', {})
                    items = body.get('items', {}).get('item', [])

                    if not items:
                        print(f"  ℹ️ page {page_no}: 항목 없음 (totalCount={body.get('totalCount')}) — 종료", flush=True)
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

                        # ── 경부선 필터 ──────────────────────────────────────
                        # API 가 전국 열차를 주므로 대상 역이 아니면 버린다.
                        # 이걸 안 걸면 하루 79만 행(전국) × 90일 ≈ 7천만 행이 쌓이는데,
                        # 정작 집계에 쓰이는 건 region_code 가 있는 경부선 역뿐이다.
                        if stn_cd_str not in target_stations:
                            skipped += 1
                            continue

                        # 전체 노선을 받으려면 위 3줄을 주석 처리한다.
                        # (그 경우 stations 에 전국 역이 쌓이고 line_nm 미제공 건은
                        #  아래 기본값 때문에 '경부선' 으로 오라벨링되니 주의.)
                        # ─────────────────────────────────────────────────────

                        # 대상 역은 seed 에 이미 있다(ON CONFLICT DO NOTHING 이라 seed 의
                        # region_code·lat·lon 은 보존된다). 만약을 위해 유지.
                        stations_to_insert.add((stn_cd_str, stn_nm_str, str(line_nm)))

                        seq_val = int(item.get('trn_run_sn') or item.get('trnRunSn') or 0)

                        actual_arr = parse_iso_time(run_ymd_param, item.get('trn_arvl_dt') or item.get('trnArvlDt'))
                        actual_dpt = parse_iso_time(run_ymd_param, item.get('trn_dptre_dt') or item.get('trnDptreDt'))
                        
                        # =====================================================================
                        # 2. CSV 파일에서 계획 시간 가져오도록 수정
                        # =====================================================================
                        csv_planned_time = get_planned_time_from_csv(trn_no, stn_nm_str, run_ymd_param)
                        
                        q['총'] += 1
                        if csv_planned_time:
                            q['CSV매칭'] += 1
                            planned_arr = csv_planned_time
                            planned_dpt = csv_planned_time
                        else:
                            # ⚠️ 예전엔 여기서 `or actual_arr` 로 실제시각을 복사했다.
                            #    그러면 delay = actual - actual = 0 이 되어, 계획시각을 못 찾은
                            #    행이 '정시 운행'으로 둔갑한다. 평균을 끌어내리고 정시율을 부풀려
                            #    특보 시 지연이 평시보다 낮게 나오는 착시를 만든다.
                            #    → 복사하지 않는다. 계획시각이 없으면 지연은 '계산 불가'다.
                            planned_arr = parse_iso_time(run_ymd_param, item.get('plt_arvl_dt') or item.get('pltArvlDt'))
                            planned_dpt = parse_iso_time(run_ymd_param, item.get('plt_dptre_dt') or item.get('pltDptreDt'))
                            if planned_arr or planned_dpt:
                                q['API계획'] += 1
                            else:
                                q['계획없음'] += 1
                        # =====================================================================

                        # event_time = **실제 기상 노출 시각** (리뷰 3.5 정의 통일).
                        #   특보 매칭은 "그 열차가 실제로 그 시각에 그 기상에 노출됐나"를 보므로
                        #   계획시각이 아니라 실제시각이 기준이다.
                        #   실적이 없으면 계획시각으로 대체한다 — 자정(00:00)으로 찍으면
                        #   엉뚱한 시간대·특보에 매칭될 수 있다.
                        #   (그런 행은 delay_min=NULL 이라 집계에서는 어차피 제외된다.)
                        event_time = (actual_arr or actual_dpt
                                      or planned_arr or planned_dpt
                                      or f"{target_date} 00:00:00+09:00")
                        train_type = classify_train_type(trn_no)

                        # ── 열차종류 필터 ────────────────────────────────────
                        # 역 기준 필터라 그 역에 서는 모든 열차가 들어온다.
                        # 서울·대전·동대구·부산역엔 무궁화·새마을도 서므로 부피가 2배가 된다
                        # (실측: KTX 92만 / 새마을 60만 / 무궁화 43만).
                        # 이 프로젝트는 '경부고속선(KTX) 10개 역'이므로 KTX 만 남긴다.
                        if train_type not in TARGET_TRAIN_TYPES:
                            skipped += 1
                            continue
                        # 모든 열차종류를 받으려면 위 3줄을 주석 처리한다.
                        # ─────────────────────────────────────────────────────

                        # 기본은 '계산 불가'. 계획·실제가 모두 있어야만 지연을 매긴다.
                        # delay_min=None → 집계의 `WHERE delay_min IS NOT NULL` 에서 자동 제외된다.
                        delay_min = None
                        status = "실적미확정"

                        pair = None
                        if actual_arr and planned_arr:
                            pair = (actual_arr, planned_arr)
                        elif actual_dpt and planned_dpt:
                            pair = (actual_dpt, planned_dpt)

                        if not (actual_arr or actual_dpt):
                            q['실제없음'] += 1

                        if pair:
                            try:
                                act_dt = datetime.fromisoformat(pair[0])
                                pln_dt = datetime.fromisoformat(pair[1])
                                diff_min = int((act_dt - pln_dt).total_seconds() / 60)
                                # 자정 넘김 보정: 계획 23:50 / 실제 익일 00:10 이면 -1420 이 된다.
                                if diff_min < -720:
                                    diff_min += 1440
                                elif diff_min > 720:
                                    diff_min -= 1440
                                delay_min = max(0, diff_min)
                                # 지연 '판정'은 운영 기준(KTX 5분)을 따른다. delay_min 자체는 원값.
                                status = "지연" if delay_min >= DELAY_THRESHOLD_MIN.get(train_type, 5) else "정상"
                                q['지연계산됨'] += 1
                            except ValueError:
                                delay_min = None
                                status = "실적미확정"
                                q['파싱오류'] += 1

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
                            ON CONFLICT (run_date, train_no, station_code) DO UPDATE SET
                                seq = EXCLUDED.seq,
                                planned_arrival = EXCLUDED.planned_arrival,
                                actual_arrival = EXCLUDED.actual_arrival,
                                planned_departure = EXCLUDED.planned_departure,
                                actual_departure = EXCLUDED.actual_departure,
                                delay_min = EXCLUDED.delay_min,
                                status = EXCLUDED.status,
                                event_time = EXCLUDED.event_time;
                        """, batch_data)
                        conn.commit()
                        print(f"✅ Page {page_no}: 경부선 {len(batch_data)}건 적재 (누적 제외 {skipped}건)")

                    total_count = body.get('totalCount', 0)
                    if page_no * num_of_rows >= total_count:
                        print(f"🏁 {target_date} 완료 — 총 {page_no}페이지 조회, 경부선 외 {skipped}건 제외")
                        break

                    page_no += 1

                except Exception as e:
                    traceback.print_exc()
                    conn.rollback()
                    failed = True
                    break

    # 성공 여부를 호출자에게 알린다. 여기서 반환을 빠뜨리면 None 이 되어
    # main 이 항상 실패로 처리한다.
    return not failed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str)
    args = parser.parse_args()
    # 실패는 반드시 종료코드로 알린다(리뷰 3.12).
    # 조용히 0 으로 끝나면 daily_update.sh 가 성공으로 보고 불완전한 데이터로 집계한다.
    ok = collect_rail_by_date(args.date)
    sys.exit(0 if ok else 1)
