import os
import pandas as pd

# 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTOR_DIR = os.path.join(BASE_DIR, 'collector')
PROCESSOR_DIR = os.path.join(BASE_DIR, 'processor')

def calculate_delay():
    print("🚀 [processor/delay.py] 열차 지연 시간(delay_min) 계산 및 정제 시작...")

    actual_path = os.path.join(COLLECTOR_DIR, 'actual_run_info_3months.csv')
    output_path = os.path.join(PROCESSOR_DIR, 'train_delay_processed.csv')

    if not os.path.exists(actual_path):
        print(f"⚠️ [오류] 원본 파일이 존재하지 않습니다: {actual_path}")
        return

    # 1. 원본 데이터 로드
    df = pd.read_csv(actual_path, low_memory=False)
    print(f"📥 원본 데이터 {len(df):,}건 로드 완료!")

    # 2. CONTRACT 명세서 기준 컬럼명 매핑
    rename_map = {
        'run_ymd': 'run_date',
        'trn_no': 'train_no',
        'trn_run_sn': 'seq',
        'stn_cd': 'station_code',
        'stn_nm': 'station_name',
        'trn_plan_arvl_dt': 'planned_arrival',
        'trn_arvl_dt': 'actual_arrival',
        'delay_minutes': 'delay_min'
    }
    df = df.rename(columns=rename_map)

    # 3. delay_min 계산
    if 'delay_min' not in df.columns:
        if 'planned_arrival' in df.columns and 'actual_arrival' in df.columns:
            planned = pd.to_datetime(df['planned_arrival'], errors='coerce')
            actual = pd.to_datetime(df['actual_arrival'], errors='coerce')
            df['delay_min'] = ((actual - planned).dt.total_seconds() / 60).fillna(0).astype(int)
        else:
            df['delay_min'] = 0

    # 조기 도착(음수)은 0분으로 보정
    df['delay_min'] = df['delay_min'].apply(lambda x: max(0, int(x)))

    if 'line' not in df.columns:
        df['line'] = '경부선'

    # 5분 이상 지연 시 '지연', 그 외는 '정상'
    df['status'] = df['delay_min'].apply(lambda x: '지연' if x >= 5 else '정상')

    # 4. 정제 완료 CSV 저장
    os.makedirs(PROCESSOR_DIR, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ [processor/delay.py] 정제 완료! 저장 위치: {output_path} ({len(df):,}건)")

if __name__ == "__main__":
    calculate_delay()