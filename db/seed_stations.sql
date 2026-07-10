INSERT INTO stations (station_code, station_name, line, seq_on_line, region_code, region_name, lat, lon) VALUES
('3900023', '서울', '경부선', 1, '11B10101', '서울', 37.554, 126.973),
('3900883', '영등포', '경부선', 2, '11B10101', '서울', 37.515, 126.907),
('3900073', '수원', '경부선', 3, '11B20601', '수원', 37.266, 126.999),
('3900096', '천안', '경부선', 4, '11C20101', '천안', 36.810, 127.147),
('3900895', '대전', '경부선', 5, '11C20401', '대전', 36.332, 127.434),
('3900896', '김천(구미)', '경부선', 6, '11H10601', '김천', 36.129, 128.114),
('3900114', '동대구', '경부선', 7, '11H10201', '대구', 35.879, 128.628),
('3900125', '밀양', '경부선', 8, '11H20401', '밀양', 35.504, 128.746),
('3900040', '부산', '경부선', 9, '11H20201', '부산', 35.115, 129.041)
ON CONFLICT (station_code) 
DO UPDATE SET 
    station_name = EXCLUDED.station_name,
    line = EXCLUDED.line,
    seq_on_line = EXCLUDED.seq_on_line,
    region_code = EXCLUDED.region_code,
    region_name = EXCLUDED.region_name,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon;