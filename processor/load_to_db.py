import os
import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from collector.db_writer import get_writer_conn

PROCESSOR_DIR = os.path.join(str(BASE_DIR), 'processor')

def load_data_to_db():
    delay_path = os.path.join(PROCESSOR_DIR, 'train_delay_processed.csv')
    vuln_path = os.path.join(PROCESSOR_DIR, 'vulnerability_processed.csv')
    
    df_vuln = pd.read_csv(vuln_path)
    df_delay = pd.read_csv(delay_path)
    
    with get_writer_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS train_delay (
                    id SERIAL PRIMARY KEY,
                    station_code VARCHAR(50),
                    station_name VARCHAR(50),
                    run_date VARCHAR(50),
                    event_time TIMESTAMPTZ,
                    delay_min FLOAT
                )
            """)
            
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='train_delay' AND column_name='event_time') THEN
                        ALTER TABLE train_delay ADD COLUMN event_time TIMESTAMPTZ;
                    END IF;
                END
                $$;
            """)
            
            cur.execute("TRUNCATE TABLE train_delay RESTART IDENTITY;")
            delay_query = """
                INSERT INTO train_delay (station_code, station_name, run_date, event_time, delay_min)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.executemany(delay_query, df_delay[['station_code', 'station_name', 'run_date', 'event_time', 'delay_min']].values.tolist())

            if not df_vuln.empty:
                vuln_query = """
                    INSERT INTO station_vulnerability (
                        station_code, alert_type, alert_level, avg_delay, delay_rate, 
                        stop_rate, sample_n, base_avg_delay, delta_delay
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (station_code, alert_type, alert_level) DO UPDATE SET
                        avg_delay = EXCLUDED.avg_delay,
                        delay_rate = EXCLUDED.delay_rate,
                        stop_rate = EXCLUDED.stop_rate,
                        sample_n = EXCLUDED.sample_n,
                        base_avg_delay = EXCLUDED.base_avg_delay,
                        delta_delay = EXCLUDED.delta_delay,
                        updated_at = now();
                """
                cur.executemany(vuln_query, df_vuln.values.tolist())
                
        conn.commit()

if __name__ == "__main__":
    load_data_to_db()