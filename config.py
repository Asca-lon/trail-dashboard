import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 경로 설정
BASE_DIR = Path(__file__).resolve().parent

# .env 파일 로드
load_dotenv(BASE_DIR / ".env")

# 1. 디렉토리 경로 정의
COLLECTOR_DIR = BASE_DIR / "collector"
DB_DIR = BASE_DIR / "db"

# 2. 데이터베이스 연결 정보
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:7784@localhost:5432/postgres"
)

# 3. API 키 및 외부 서비스 URL
PUBLIC_DATA_API_KEY = os.getenv("PUBLIC_DATA_API_KEY")
KORAIL_RUN_API_URL = os.getenv("KORail_RUN_API_URL", "https://apis.data.go.kr/B551457/run/v2").rstrip('/')
MOLIT_TRAIN_API_URL = os.getenv("MOLIT_TRAIN_API_URL", "https://apis.data.go.kr/1613000/TrainInfo").rstrip('/')

KMA_API_KEY = os.getenv("KMA_API_KEY")
KMA_WRN_REG_URL = os.getenv("KMA_WRN_REG_URL", "https://apihub.kma.go.kr/api/typ01/url/wrn_reg.php")
KMA_WRN_DATA_URL = os.getenv("KMA_WRN_DATA_URL", "https://apihub.kma.go.kr/api/typ01/url/wrn_met_data.php")
KMA_WRN_INF_URL = os.getenv("KMA_WRN_INF_URL", "https://apihub.kma.go.kr/api/typ01/url/wrn_inf_rpt.php")
KMA_WTHR_CMT_URL = os.getenv("KMA_WTHR_CMT_URL", "https://apihub.kma.go.kr/api/typ01/url/wthr_cmt_rpt.php")

# 4. 원천 CSV 파일 경로 정의
ACTUAL_RUN_INFO_PATH = COLLECTOR_DIR / "actual_run_info_3months.csv"
PLAN_INFO_PATH = COLLECTOR_DIR / "gyeongbu_line_total(plan).csv"
WEATHER_WARNING_PATH = COLLECTOR_DIR / "weather_warning_3months.csv"
TAGO_STATION_PATH = COLLECTOR_DIR / "tago_gyeongbu_station.csv"
TAGO_LINE_PATH = COLLECTOR_DIR / "tago_gyeongbu_line.csv"