import os
import sys
import requests
import traceback
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn

KMA_API_KEY = os.getenv("KMA_API_KEY")
KMA_WRN_DATA_URL = os.getenv("KMA_WRN_DATA_URL", "https://apihub.kma.go.kr/api/typ01/url/wrn_met_data.php")

WRN_CD_MAP = {
    '1': ('강풍', '주의보'), '2': ('호우', '주의보'), '3': ('한파', '주의보'),
    '4': ('태풍', '주의보'), '5': ('대설', '주의보'), '6': ('황사', '주의보'),
    '7': ('폭염', '주의보'), '12': ('호우', '경보'), '17': ('폭염', '경보')
}

def parse_kma_time(tm_str):
    if not tm_str or len(tm_str) < 12:
        return None
    s = tm_str.strip()
    return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:00+09:00"

def collect_realtime_weather():
    if not KMA_API_KEY:
        print("❌ KMA_API_KEY가 설정되지 않았습니다.")
        return

    params = {
        'authKey': KMA_API_KEY,
        'disp': '0',
        'help': '0'
    }

    try:
        response = requests.get(KMA_WRN_DATA_URL, params=params, timeout=10)

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            data_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

            if not data_lines:
                print("ℹ️ 수집할 기상 데이터가 없습니다.")
                return

            batch_data = []
            for line in data_lines:
                # 콤마(,) 기준으로 분할 후 공백 제거
                cols = [c.strip() for c in line.split(',')]
                if len(cols) < 7:
                    continue

                tm_fc = parse_kma_time(cols[0])
                region_code = cols[4]  # L1020800 형태의 지역코드
                wrn_cd = cols[6]       # 특보 코드 (2, 7 등)

                alert_info = WRN_CD_MAP.get(wrn_cd)
                if not alert_info:
                    continue

                alert_type, alert_level = alert_info

                if alert_type not in ['호우', '폭염']:
                    continue

                if not tm_fc or not region_code:
                    continue

                batch_data.append((region_code, alert_type, alert_level, tm_fc, None))

            if batch_data:
                with get_writer_conn() as conn:
                    with conn.cursor() as cur:
                        cur.executemany("""
                            INSERT INTO weather_alerts (region_code, alert_type, alert_level, start_time, end_time)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (region_code, alert_type, alert_level, start_time) DO NOTHING;
                        """, batch_data)
                        conn.commit()
                        print(f"✅ 기상 특보 {len(batch_data)}건 확인 및 적재 완료!")
            else:
                print("ℹ️ 현재 조건(호우/폭염)에 일치하는 특보가 없습니다.")

    except Exception as e:
        print(f"❌ 기상 데이터 수집 중 오류 발생: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    collect_realtime_weather()