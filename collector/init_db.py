"""
collector/init_db.py — 3개월치 CSV 초기 데이터 DB 적재
"""
import os
import pandas as pd
from config import ACTUAL_RUN_INFO_PATH, WEATHER_WARNING_PATH
from db_writer import get_writer_conn

def parse_ktx_excel(filepath):
    """KTX/SRT 시각표 엑셀 파싱"""
    df_ktx = pd.read_excel(filepath, sheet_name='경부선')
    stn_down = df_ktx.iloc[6, 1:24].values
    stn_up = df_ktx.iloc[6, 26:49].values
    
    records = []
    
    # 하행 파싱
    for idx, row in df_ktx.iloc[9:].iterrows():
        trn_no = row.iloc[1]
        if pd.isna(trn_no) or not str(trn_no).strip().isdigit():
            continue
        trn_no = str(int(trn_no))
        train_grade = str(row.iloc[2]).strip()
        
        for col_i, stn_name in enumerate(stn_down[2:], start=3):
            time_val = row.iloc[col_i]
            if pd.notnull(time_val) and str(time_val).strip() != '00:00:00':
                records.append({
                    'trn_no': trn_no,
                    'train_grade': train_grade,
                    'stn_nm': str(stn_name).strip(),
                    'plan_time': str(time_val).strip()
                })
                
    # 상행 파싱
    for idx, row in df_ktx.iloc[9:].iterrows():
        trn_no = row.iloc[26]
        if pd.isna(trn_no) or not str(trn_no).strip().isdigit():
            continue
        trn_no = str(int(trn_no))
        train_grade = str(row.iloc[27]).strip()
        
        for col_i, stn_name in enumerate(stn_up[2:], start=28):
            time_val = row.iloc[col_i]
            if pd.notnull(time_val) and str(time_val).strip() != '00:00:00':
                records.append({
                    'trn_no': trn_no,
                    'train_grade': train_grade,
                    'stn_nm': str(stn_name).strip(),
                    'plan_time': str(time_val).strip()
                })
                
    return pd.DataFrame(records)

def parse_general_excel(filepath):
    """일반열차 시각표 엑셀 파싱"""
    xl = pd.ExcelFile(filepath)
    records = []
    
    for sheet in xl.sheet_names:
        if sheet == '보는방법' or '경부' not in sheet:
            continue
        df_s = pd.read_excel(filepath, sheet_name=sheet)
        
        for col_idx in range(1, df_s.shape[1]):
            trn_no = df_s.iloc[7, col_idx] if len(df_s) > 7 else None
            train_grade = df_s.iloc[6, col_idx] if len(df_s) > 6 else '일반열차'
            
            if pd.notnull(trn_no) and str(trn_no).strip().isdigit():
                trn_no = str(int(trn_no))
                for row_idx in range(8, len(df_s)):
                    stn_nm = df_s.iloc[row_idx, 0]
                    time_val = df_s.iloc[row_idx, col_idx]
                    if pd.notnull(stn_nm) and pd.notnull(time_val) and str(time_val).strip() != '00:00:00':
                        records.append({
                            'trn_no': trn_no,
                            'train_grade': str(train_grade).strip(),
                            'stn_nm': str(stn_nm).strip(),
                            'plan_time': str(time_val).strip()
                        })
                        
    return pd.DataFrame(records)

def init_3months_data():
    print("🚀 [초기 적재] 3개월치 원천 CSV 및 공식 시각표 DB 적재 시작...")

    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            # 0. 공식 시각표 Master 테이블 생성 (없을 경우)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS train_schedules (
                    trn_no VARCHAR(20),
                    train_grade VARCHAR(50),
                    stn_nm VARCHAR(50),
                    plan_time VARCHAR(20),
                    PRIMARY KEY (trn_no, stn_nm)
                );
            """)

            # 1. 공식 시각표 엑셀 파일 적재
            file_ktx = "2026042419dbe8dce18380.xlsx"
            file_gen = "2026032619d273b8a4750.xlsx"

            if os.path.exists(file_ktx) and os.path.exists(file_gen):
                print("  ├ 📋 코레일 공식 정기 시각표 엑셀 처리 중...")
                df_ktx = parse_ktx_excel(file_ktx)
                df_gen = parse_general_excel(file_gen)
                
                df_master = pd.concat([df_ktx, df_gen], ignore_index=True).drop_duplicates(subset=['trn_no', 'stn_nm'])
                df_master = df_master.where(pd.notnull(df_master), None)

                for _, r in df_master.iterrows():
                    cur.execute("""
                        INSERT INTO train_schedules (trn_no, train_grade, stn_nm, plan_time)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (trn_no, stn_nm) DO UPDATE 
                        SET train_grade = EXCLUDED.train_grade, plan_time = EXCLUDED.plan_time;
                    """, (r.get('trn_no'), r.get('train_grade'), r.get('stn_nm'), r.get('plan_time')))
                
                print(f"  └ [성공] 공식 정기 시각표 {len(df_master):,}건 적재 완료")

            # 2. 기상 특보 데이터 적재
            if os.path.exists(WEATHER_WARNING_PATH):
                print("  ├ 🌤️ 기상 특보 데이터 처리 중...")
                df_w = pd.read_csv(WEATHER_WARNING_PATH)
                df_w = df_w.rename(columns={
                    '발표 날짜': 'tm_fc', '특보 종류': 'wrn_cd', '특보 등급': 'lvl',
                    '발효 지역': 'reg_id', '발효 시각': 'tm_seq', '해제 시각': 'shrt_seq'
                })
                df_w['tm_fc'] = pd.to_datetime(df_w['tm_fc'].astype(str), format='%Y%m%d%H%M', errors='coerce').astype(str)
                df_w = df_w.where(pd.notnull(df_w), None)
                
                for _, r in df_w.iterrows():
                    cur.execute("""
                        INSERT INTO weather_alerts (tm_fc, wrn_cd, lvl, reg_id, tm_seq, shrt_seq)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (
                        r.get('tm_fc'), r.get('wrn_cd'), r.get('lvl'), 
                        r.get('reg_id'), r.get('tm_seq'), r.get('shrt_seq')
                    ))
                print(f"  └ [성공] 기상 특보 {len(df_w):,}건 적재 완료")

            # 3. 실제 운행 데이터 적재
            if os.path.exists(ACTUAL_RUN_INFO_PATH):
                print("  ├ 🚆 철도 실제 운행 데이터 처리 중...")
                df_r = pd.read_csv(ACTUAL_RUN_INFO_PATH, dtype={'mrnt_cd': str, 'stn_cd': str, 'trn_no': str})
                df_r['run_ymd'] = pd.to_datetime(df_r['run_ymd'].astype(str), format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')
                df_r = df_r.where(pd.notnull(df_r), None)
                
                for _, r in df_r.iterrows():
                    cur.execute("""
                        INSERT INTO train_stops (
                            mrnt_cd, mrnt_nm, run_ymd, stn_cd, stn_nm, 
                            stop_se_cd, stop_se_nm, trn_arvl_dt, trn_dptre_dt, 
                            trn_no, trn_run_sn, uppln_dn_se_cd
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        r.get('mrnt_cd'), r.get('mrnt_nm'), r.get('run_ymd'), 
                        r.get('stn_cd'), r.get('stn_nm'), r.get('stop_se_cd'), 
                        r.get('stop_se_nm'), r.get('trn_arvl_dt'), r.get('trn_dptre_dt'), 
                        r.get('trn_no'), r.get('trn_run_sn'), r.get('uppln_dn_se_cd')
                    ))
                print(f"  └ [성공] 철도 운행 데이터 {len(df_r):,}건 적재 완료")

    print("🎉 [완료] 3개월 초기 적재 및 시각표 적재 작업이 성공적으로 끝났습니다.")

if __name__ == "__main__":
    init_3months_data()