"""
collector/db_writer.py — 수집기 전용 DB 쓰기(INSERT/UPSERT) 커넥션 모듈
"""
import os
from pathlib import Path
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# 프로젝트 루트의 .env 읽기
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # 기본값은 compose DB(trail). .env 가 있으면 그 값이 우선한다.
    "postgresql://trail:trail@localhost:5432/trail",
)

# 별칭: processor 등에서 SQLAlchemy create_engine(DB_URL) 에 쓰는 URL 문자열.
# vulnerability.py 가 이 이름을 import 한다. DATABASE_URL 과 같은 값.
DB_URL = DATABASE_URL

@contextmanager
def get_writer_conn():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
