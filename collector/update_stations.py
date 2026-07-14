import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn

station_updates = [
    ('서울', 1, '108', '서울'), ('용산', 2, '108', '서울'), ('영등포', 3, '108', '서울'),
    ('광명', 4, '119', '경기'), ('안양', 5, '119', '경기'), ('수원', 6, '119', '경기'),
    ('오산', 7, '119', '경기'), ('서정리', 8, '119', '경기'), ('평택', 9, '119', '경기'),
    ('천안아산', 10, '232', '충남'), ('천안', 11, '232', '충남'), ('조치원', 12, '239', '세종'),
    ('오송', 13, '131', '충북'), ('대전', 14, '133', '대전'), ('옥천', 15, '133', '충북'),
    ('영동', 16, '133', '충북'), ('김천', 17, '279', '경북'), ('김천구미', 18, '279', '경북'),
    ('구미', 19, '279', '경북'), ('왜관', 20, '279', '경북'), ('서대구', 21, '143', '대구'),
    ('동대구', 22, '143', '대구'), ('대구', 23, '143', '대구'), ('경산', 24, '281', '경북'),
    ('경주', 25, '283', '경북'), ('울산', 26, '152', '울산'), ('밀양', 27, '288', '경남'),
    ('물금', 28, '288', '경남'), ('구포', 29, '159', '부산'), ('사상', 30, '159', '부산'),
    ('부산', 31, '159', '부산')
]

def update_stations():
    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            for stn_nm, seq, reg_cd, reg_nm in station_updates:
                cur.execute(
                    "UPDATE stations SET seq_on_line=%s, region_code=%s, region_name=%s WHERE station_name=%s", 
                    (seq, reg_cd, reg_nm, stn_nm)
                )
        conn.commit()
    print("✅ 완벽한 역 정보(순서 및 기상코드) 업데이트 완료!")

if __name__ == "__main__":
    update_stations()