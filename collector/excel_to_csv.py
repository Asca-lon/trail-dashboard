import pandas as pd
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COLLECTOR_DIR = str(BASE_DIR)

def process_ktx(filepath):
    df = pd.read_excel(filepath, sheet_name='경부선', header=7)
    train_cols = [i for i, col in enumerate(df.columns) if '열차번호' in str(col)]
    bigo_cols = [i for i, col in enumerate(df.columns) if '비고' in str(col)]
    records = []
    
    if len(train_cols) >= 2 and len(bigo_cols) >= 2:
        down_df = df.iloc[:, train_cols[0]:bigo_cols[0]+1].copy()
        down_df['direction'] = 'down'
        
        up_df = df.iloc[:, train_cols[1]:bigo_cols[1]+1].copy()
        up_df['direction'] = 'up'
        
        down_df.columns = [re.sub(r'\.\d+$', '', str(c)) for c in down_df.columns]
        up_df.columns = [re.sub(r'\.\d+$', '', str(c)) for c in up_df.columns]
        
        records.extend([down_df, up_df])
        
    return records

def process_general(filepath):
    df = pd.read_excel(filepath, sheet_name='경부선', header=None)
    train_types = df.iloc[7]
    train_nos = df.iloc[8]
    records_list = []
    
    for col_idx in range(len(train_nos)):
        if pd.notna(train_nos[col_idx]) and str(train_nos[col_idx]).strip().isdigit():
            record = {
                '열차번호': str(int(train_nos[col_idx])),
                '편성': train_types[col_idx],
                'direction': 'down'
            }
            
            for row_idx in range(9, len(df)):
                stn = str(df.iloc[row_idx, 0]).strip().replace(' ', '')
                
                if stn in ['nan', '시발역', '종착역', '열차종별'] or '비고' in stn:
                    continue
                    
                val = df.iloc[row_idx, col_idx]
                
                if pd.notna(val) and str(val).strip() not in ['00:00:00', '']:
                    record[stn] = str(val).strip()
                    
            records_list.append(record)
            
    return [pd.DataFrame(records_list)]

def clean_excel():
    all_data = []
    ktx_file = os.path.join(COLLECTOR_DIR, '2026042419dbe8dce18380.xlsx')
    gen_file = os.path.join(COLLECTOR_DIR, '2026032619d273b8a4750.xlsx')
    
    if os.path.exists(ktx_file):
        all_data.extend(process_ktx(ktx_file))
        
    if os.path.exists(gen_file):
        all_data.extend(process_general(gen_file))
        
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        output_path = os.path.join(COLLECTOR_DIR, 'gyeongbu_plan_total.csv')
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print("✅ 시간표 통합 완료.")

if __name__ == "__main__":
    clean_excel()