"""
db.py — 조회 전용 DB 접근.

경계선(§2-1): B는 DB에 **쓰지 않는다.** A가 채운 테이블을 읽기만 한다.
- station_vulnerability / segment_vulnerability : A(분석) 산출물
- train_stops / stations / weather_alerts : A 적재

USE_MOCK=1 이면 이 모듈은 아예 안 쓰인다(api.py 가 mock/*.json 을 응답).
A의 집계가 채워지기 전까지는 USE_MOCK=1 로 워킹 스켈레톤을 돌린다.
"""
from __future__ import annotations
import os
from contextlib import contextmanager

# psycopg (v3). requirements.txt 참고.
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://readonly:readonly@localhost:5432/trail",
)


@contextmanager
def get_conn():
    """
    조회 전용 커넥션. 가능하면 DB 계정 자체를 읽기 전용으로 발급받는다:
        CREATE ROLE readonly LOGIN PASSWORD '...';
        GRANT CONNECT ON DATABASE trail TO readonly;
        GRANT USAGE ON SCHEMA public TO readonly;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
    권한 수준에서 쓰기를 막아두면 계약 위반이 원천 차단된다.
    """
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        # 세션을 읽기 전용으로 고정 — 실수로도 write 불가.
        conn.execute("SET default_transaction_read_only = on;")
        yield conn
    finally:
        conn.close()


def fetch_all(sql: str, params: dict | tuple | None = None) -> list[dict]:
    with get_conn() as conn:
        cur = conn.execute(sql, params or {})
        return cur.fetchall()


def fetch_one(sql: str, params: dict | tuple | None = None) -> dict | None:
    with get_conn() as conn:
        cur = conn.execute(sql, params or {})
        return cur.fetchone()
