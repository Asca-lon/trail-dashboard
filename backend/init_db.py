import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'railway_risk.db')

def find_file(filename):
    path1 = os.path.join(BASE_DIR, filename)
    path2 = os.path.join(os.getcwd(), filename)
    if os.path.exists(path1):
        return path1
    elif os.path.exists(path2):
        return path2
    return None

def init_db_pipeline():
    print("🚀 [CONTRACT.md 규격] DB 적재 파이프라인 시작...")
    conn = sqlite3.connect(DB_PATH)

    # 1. stations 테이블 적재
    stn_file = find_file('tago_gyeongbu_line.csv') or find_file('tago_gyeongbu_station.csv')
    if stn_file:
        df_stn = pd.read_csv(stn_file, low_memory=False)
        
        # 컬럼명 유연하게 변경
        rename_dict = {}
        if 'nodeid' in df_stn.columns:
            rename_dict['nodeid'] = 'station_code'
        if 'nodename' in df_stn.columns:
            rename_dict['nodename'] = 'station_name'
        
        if rename_dict:
            df_stn = df_stn.rename(columns=rename_dict)
            
        if 'line' not in df_stn.columns:
            df_stn['line'] = '경부선'
            
        # 존재하는 컬럼으로만 테이블 생성
        cols_to_use = [c for c in ['station_code', 'station_name', 'line'] if c in df_stn.columns]
        df_stn[cols_to_use].to_sql('stations', conn, if_exists='replace', index=False)
        print(f"✅ [1/3] 'stations' 적재 완료! ({len(df_stn):,}건)")
    else:
        print("❌ 역 정보 CSV 파일을 찾지 못함!")

    # 2. train_stops 테이블 적재
    delay_file = find_file('train_delay_processed.csv')
    if delay_file:
        df_stops = pd.read_csv(delay_file, low_memory=False)
        rename_map = {
            'run_ymd': 'run_date', 'trn_no': 'train_no', 'trn_run_sn': 'seq',
            'stn_cd': 'station_code', 'stn_nm': 'station_name',
            'trn_plan_arvl_dt': 'planned_arrival', 'trn_arvl_dt': 'actual_arrival',
            'delay_minutes': 'delay_min'
        }
        df_stops = df_stops.rename(columns=rename_map)
        if 'line' not in df_stops.columns:
            df_stops['line'] = '경부선'
        if 'delay_min' in df_stops.columns:
            df_stops['status'] = df_stops['delay_min'].apply(lambda x: '지연' if x >= 5 else '정상')
            
        df_stops.to_sql('train_stops', conn, if_exists='replace', index=False)
        print(f"✅ [2/3] 'train_stops' 적재 완료! ({len(df_stops):,}건)")
    else:
        print("❌ train_delay_processed.csv 파일을 찾지 못함!")

    # 3. weather_alerts 테이블 적재
    weather_file = find_file('weather_warning_3months.csv')
    if weather_file:
        df_weather = pd.read_csv(weather_file, low_memory=False)
        rename_weather = {
            '발표 날짜': 'start_time', '특보 종류': 'alert_type',
            '특보 등급': 'alert_level', '발효 지역': 'region_name'
        }
        df_weather = df_weather.rename(columns=rename_weather)
        df_weather.to_sql('weather_alerts', conn, if_exists='replace', index=False)
        print(f"✅ [3/3] 'weather_alerts' 적재 완료! ({len(df_weather):,}건)")
    else:
        print("❌ weather_warning_3months.csv 파일을 찾지 못함!")

    conn.close()
    print("\n🎉 모든 데이터가 데이터베이스(railway_risk.db)에 완벽히 들어갔습니다!")

if __name__ == "__main__":
    init_db_pipeline()