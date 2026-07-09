import os
import requests
from dotenv import load_dotenv
from db_writer import get_writer_conn

# .env 파일 로드
load_dotenv()

# .env에서 공공데이터포털 API 키 및 철도 운행 Base URL 가져오기
PUBLIC_API_KEY = os.getenv("PUBLIC_DATA_API_KEY", "416ae05cbf69b4c9b3c32cdc101a39a774f304c9c0d0d806362af53cc9ee31b2")
KORAIL_RUN_API_URL = os.getenv("KORail_RUN_API_URL", "https://apis.data.go.kr/B551457/run/v2").rstrip('/')

def collect_realtime_rail():
    print("🚆 [실시간 철도] 최신 여객열차 운행정보 수집 중...")
    
    url = f"{KORAIL_RUN_API_URL}/travelerTrainRunInfo2"
    
    params = {
        'serviceKey': requests.utils.unquote(PUBLIC_API_KEY),
        'pageNo': '1',
        'numOfRows': '100',
        '_type': 'json'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"  ├ 🌐 API 응답 상태 코드: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                print(f"  └ 🚨 JSON 파싱 실패 (응답 내용: {response.text[:200]})")
                return

            header = data.get('response', {}).get('header', {})
            result_code = header.get('resultCode')
            result_msg = header.get('resultMsg')

            # '0' 또는 '00' 모두 정상으로 처리
            if str(result_code) not in ['0', '00']:
                print(f"  └ 🚨 API 결과 에러: [{result_code}] {result_msg}")
                return

            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            
            if items:
                if isinstance(items, dict):
                    items = [items]

                inserted_cnt = 0
                with get_writer_conn() as conn:
                    with conn.cursor() as cur:
                        for item in items:
                            run_ymd = item.get('runYmd') or item.get('run_ymd')
                            trn_no = item.get('trnNo') or item.get('trn_no')
                            stn_cd = item.get('stnCd') or item.get('stn_cd')

                            if not run_ymd or not trn_no or not stn_cd:
                                continue

                            cur.execute("""
                                INSERT INTO train_stops (
                                    mrnt_cd, mrnt_nm, run_ymd, stn_cd, stn_nm,
                                    stop_se_cd, stop_se_nm, trn_arvl_dt, trn_dptre_dt,
                                    trn_no, trn_run_sn, uppln_dn_se_cd
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING;
                            """, (
                                item.get('mrntCd'), item.get('mrntNm'), run_ymd,
                                stn_cd, item.get('stnNm'), item.get('stopSeCd'),
                                item.get('stopSeNm'), item.get('trnArvlDt'), item.get('trnDptreDt'),
                                trn_no, item.get('trnRunSn'), item.get('upplnDnSeCd')
                            ))
                            inserted_cnt += 1

                print(f"🎉 [성공] 철도 운행 데이터 {inserted_cnt}건 동기화 완료!")
            else:
                print("  └ ℹ️ 현재 수집된 철도 운행 데이터가 없습니다.")
        else:
            print(f"  └ 🚨 API 요청 실패 (HTTP {response.status_code})")

    except Exception as e:
        print(f"💥 수집 예외 발생: {e}")

if __name__ == "__main__":
    collect_realtime_rail()