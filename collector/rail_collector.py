import pandas as pd
import os
from config import ACTUAL_RUN_INFO_PATH, PLAN_INFO_PATH

def fetch_rail_data():
    """
    운행계획 및 실제 운행정보 CSV 데이터를 읽어오는 수집 모듈
    """
    print("📥 [collector/rail_collector.py] 철도 운행 데이터 수집 및 로드 시작...")

    if not os.path.exists(ACTUAL_RUN_INFO_PATH):
        print(f"⚠️ [오류] 운행 정보 파일이 없습니다: {ACTUAL_RUN_INFO_PATH}")
        return None

    # 실제 운행 데이터 로드
    df_actual = pd.read_csv(ACTUAL_RUN_INFO_PATH, low_memory=False)
    print(f"✅ 실제 운행 데이터 로드 완료: 총 {len(df_actual):,}건")

    return df_actual

if __name__ == "__main__":
    df = fetch_rail_data()