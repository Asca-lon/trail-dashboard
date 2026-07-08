import pandas as pd
import os
from config import WEATHER_WARNING_PATH

def fetch_weather_data():
    """
    기상 특보 이력 원천 CSV 데이터를 읽어오는 수집 모듈
    """
    print("🌤️ [collector/weather_collector.py] 기상 특보 데이터 수집 및 로드 시작...")

    if not os.path.exists(WEATHER_WARNING_PATH):
        print(f"⚠️ [오류] 기상 특보 파일이 없습니다: {WEATHER_WARNING_PATH}")
        return None

    # 기상 특보 데이터 로드
    df_weather = pd.read_csv(WEATHER_WARNING_PATH, low_memory=False)
    print(f"✅ 기상 특보 데이터 로드 완료: 총 {len(df_weather):,}건")

    return df_weather

if __name__ == "__main__":
    df = fetch_weather_data()