"""
collector/db_writer.py — 수집기 전용 DB 쓰기(INSERT/UPSERT) 커넥션 모듈
"""
import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:7784@localhost:5432/postgres", # 쓰기 권한 계정 URL
)

@contextmanager
def get_writer_conn():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()