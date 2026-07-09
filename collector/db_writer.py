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
    "postgresql://postgres:7784@localhost:5432/postgres",
)

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