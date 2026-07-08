import os

# collector 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTOR_DIR = os.path.join(BASE_DIR, 'collector')

# 원천 CSV 파일 경로 정의
ACTUAL_RUN_INFO_PATH = os.path.join(COLLECTOR_DIR, 'actual_run_info_3months.csv')
PLAN_INFO_PATH = os.path.join(COLLECTOR_DIR, 'gyeongbu_line_total(plan).csv')
WEATHER_WARNING_PATH = os.path.join(COLLECTOR_DIR, 'weather_warning_3months.csv')
TAGO_STATION_PATH = os.path.join(COLLECTOR_DIR, 'tago_gyeongbu_station.csv')
TAGO_LINE_PATH = os.path.join(COLLECTOR_DIR, 'tago_gyeongbu_line.csv')