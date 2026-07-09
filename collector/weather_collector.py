import os
import requests
from dotenv import load_dotenv
from db_writer import get_writer_conn

load_dotenv()

# .env에서 기상청 API Hub 키 및 URL 가져오기
KMA_API_KEY = os.getenv("KMA_API_KEY", "kMT3q11PQXmE96tdTyF5Ow")
KMA_WRN_DATA_URL = os.getenv("KMA_WRN_DATA_URL", "https://apihub.kma.go.kr/api/typ01/url/wrn_met_data.php")

def parse_kma_time(tm_str):
    """YYYYMMDDHHMM 포맷 변환"""
    if not tm_str or len(tm_str) < 12:
        return None
    s = tm_str.strip()
    return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:00"

def collect_realtime_weather():
    print("📡 [실시간 기상] 기상청 API Hub 최신 특보 데이터 수집 중...")
    
    # API Hub 매개변수 설정
    params = {
        'authKey': KMA_API_KEY,
        'disp': '0',        # 0: 텍스트/CSV 형태 파싱
        'help': '0'
    }

    try:
        response = requests.get(KMA_WRN_DATA_URL, params=params, timeout=10)
        print(f"  ├ 🌐 API 응답 상태 코드: {response.status_code}")

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            data_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

            if not data_lines:
                print("  └ ℹ️ 현재 발효 중인 기상 특보 데이터가 없습니다.")
                return

            inserted_cnt = 0
            with get_writer_conn() as conn:
                with conn.cursor() as cur:
                    for line in data_lines:
                        # API Hub 데이터 공백 기준 분할
                        cols = line.split()
                        if len(cols) < 6:
                            continue

                        tm_fc = parse_kma_time(cols[0])
                        reg_id = cols[1]
                        wrn_cd = cols[2]
                        lvl = cols[3]
                        tm_seq = cols[4] if cols[4].isdigit() else 0
                        shrt_seq = cols[5] if cols[5].isdigit() else 0

                        if not tm_fc or not reg_id or not wrn_cd:
                            continue

                        cur.execute("""
                            INSERT INTO weather_alerts (tm_fc, wrn_cd, lvl, reg_id, tm_seq, shrt_seq)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (tm_fc, reg_id, wrn_cd) 
                            DO UPDATE SET lvl = EXCLUDED.lvl, shrt_seq = EXCLUDED.shrt_seq;
                        """, (tm_fc, wrn_cd, lvl, reg_id, tm_seq, shrt_seq))
                        inserted_cnt += 1

            print(f"🎉 [성공] 기상 특보 {inserted_cnt}건 동기화 완료!")
        else:
            print(f"  └ 🚨 API 요청 실패 (HTTP {response.status_code})")

    except Exception as e:
        print(f"💥 수집 예외 발생: {e}")

if __name__ == "__main__":
    collect_realtime_weather()