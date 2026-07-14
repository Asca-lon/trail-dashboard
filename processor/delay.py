import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
COLLECTOR_DIR = os.path.join(str(BASE_DIR), 'collector')
PROCESSOR_DIR = os.path.join(str(BASE_DIR), 'processor')

def process_delay():
    plan_path = os.path.join(COLLECTOR_DIR, 'gyeongbu_plan_total.csv')
    actual_path = os.path.join(COLLECTOR_DIR, 'actual_run_info_3months.csv')
    output_path = os.path.join(PROCESSOR_DIR, 'train_delay_processed.csv')

    df_plan = pd.read_csv(plan_path, encoding='utf-8-sig')
    id_vars = ['열차번호', '편성', '비고', 'direction', '비고(정차역)']
    station_cols = [c for c in df_plan.columns if c not in id_vars]

    df_plan_melted = df_plan.melt(
        id_vars=['열차번호'],
        value_vars=station_cols,
        var_name='station_name',
        value_name='plan_time'
    )
    df_plan_melted = df_plan_melted.dropna(subset=['plan_time'])
    df_plan_melted = df_plan_melted[df_plan_melted['plan_time'] != '00:00:00']
    df_plan_melted['열차번호'] = df_plan_melted['열차번호'].astype(str).str.split('.').str[0]

    df_actual = pd.read_csv(actual_path, encoding='utf-8-sig', on_bad_lines='skip', dtype={'mrnt_cd': str}, low_memory=False)
    df_actual['trn_no'] = df_actual['trn_no'].astype(str).str.split('.').str[0]

    df_merged = pd.merge(
        df_actual,
        df_plan_melted,
        left_on=['trn_no', 'stn_nm'],
        right_on=['열차번호', 'station_name'],
        how='inner'
    )

    df_merged['actual_dt'] = pd.to_datetime(df_merged['trn_dptre_dt'].fillna(df_merged['trn_arvl_dt']))
    df_merged['plan_dt'] = pd.to_datetime(
        df_merged['run_ymd'].astype(str) + ' ' + df_merged['plan_time'],
        format='%Y%m%d %H:%M:%S',
        errors='coerce'
    )

    df_merged['delay_min'] = (df_merged['actual_dt'] - df_merged['plan_dt']).dt.total_seconds() / 60
    df_merged.loc[df_merged['delay_min'] < -500, 'delay_min'] += 1440
    df_merged['delay_min'] = df_merged['delay_min'].apply(lambda x: max(0, x)).round(1)

    result_df = df_merged[['stn_cd', 'stn_nm', 'run_ymd', 'actual_dt', 'delay_min']].copy()
    result_df.rename(columns={'stn_cd': 'station_code', 'stn_nm': 'station_name', 'run_ymd': 'run_date', 'actual_dt': 'event_time'}, inplace=True)
    result_df = result_df.dropna(subset=['event_time'])

    os.makedirs(PROCESSOR_DIR, exist_ok=True)
    result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    process_delay()