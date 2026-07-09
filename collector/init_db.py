import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn

def run_sql_file(cur, file_path):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())

def init_database():
    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            run_sql_file(cur, BASE_DIR / "db" / "init_schema.sql")
            run_sql_file(cur, BASE_DIR / "db" / "seed_stations.sql")
            conn.commit()

if __name__ == "__main__":
    init_database()