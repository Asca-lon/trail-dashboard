#!/usr/bin/env bash
# setup_detail.sh — 상세 화면 mock 2개 추가 + api.py 연결 + 테스트 등록.
# setup_dev.sh 를 먼저 적용한 뒤, 레포 루트에서 실행:  bash setup_detail.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; cd "$ROOT"
echo ">>> 레포 루트: $ROOT"

# ── 1) mock/station_detail.json ───────────────────────────────
cat > mock/station_detail.json << 'EOF'
{
  "station": "대전",
  "by_alert": [
    { "alert_type": "호우", "alert_level": "경보",   "avg_delay": 15.2, "sample_n": 34 },
    { "alert_type": "폭염", "alert_level": "경보",   "avg_delay": 12.7, "sample_n": 61 },
    { "alert_type": "호우", "alert_level": "주의보", "avg_delay": 8.4,  "sample_n": 52 },
    { "alert_type": "폭염", "alert_level": "주의보", "avg_delay": 6.1,  "sample_n": 70 }
  ],
  "cases": [
    { "date": "2026-06-28", "alert_type": "호우", "delay_min": 22 },
    { "date": "2026-06-22", "alert_type": "폭염", "delay_min": 15 },
    { "date": "2026-06-15", "alert_type": "호우", "delay_min": 11 },
    { "date": "2026-06-09", "alert_type": null,   "delay_min": 7 }
  ]
}
EOF

# ── 2) mock/segment_detail.json ───────────────────────────────
cat > mock/segment_detail.json << 'EOF'
{
  "from": "대전",
  "to": "김천(구미)",
  "by_alert": [
    { "alert_type": "호우", "alert_level": "경보",   "avg_delay": 14.6, "sample_n": 37 },
    { "alert_type": "호우", "alert_level": "주의보", "avg_delay": 9.1,  "sample_n": 44 },
    { "alert_type": "폭염", "alert_level": "경보",   "avg_delay": 7.2,  "sample_n": 25 }
  ],
  "cases": [
    { "date": "2026-06-28", "alert_type": "호우", "delay_min": 19 },
    { "date": "2026-06-14", "alert_type": "호우", "delay_min": 12 },
    { "date": "2026-06-03", "alert_type": null,   "delay_min": 6 }
  ]
}
EOF

# ── 3) api.py: 상세 스텁 -> mock 파일 반환으로 교체 ────────────
python3 - << 'PY'
from pathlib import Path
p = Path("backend/api.py"); s = p.read_text(encoding="utf-8")

st_old = ('    if USE_MOCK:\n'
          '        # 정적 mock 없음: 스켈레톤에선 빈 상세를 계약 모양으로 반환.\n'
          '        return {"station": code, "by_alert": [], "cases": []}')
st_new = ('    if USE_MOCK:\n'
          '        d = _mock("station_detail.json")\n'
          '        d["station"] = code   # 어떤 역을 조회하든 상세 모양을 보여준다(값은 mock)\n'
          '        return d')

sg_old = ('    if USE_MOCK:\n'
          '        return {"from": frm, "to": to, "by_alert": [], "cases": []}')
sg_new = ('    if USE_MOCK:\n'
          '        d = _mock("segment_detail.json")\n'
          '        d["from"], d["to"] = frm, to\n'
          '        return d')

changed = False
if st_old in s:
    s = s.replace(st_old, st_new); changed = True; print("  api.py: station 상세 연결")
elif 'station_detail.json' in s:
    print("  api.py: station 이미 연결됨(건너뜀)")
else:
    raise SystemExit("  [경고] station 상세 스텁을 못 찾음 — 수동 확인 필요")

if sg_old in s:
    s = s.replace(sg_old, sg_new); changed = True; print("  api.py: segment 상세 연결")
elif 'segment_detail.json' in s:
    print("  api.py: segment 이미 연결됨(건너뜀)")
else:
    raise SystemExit("  [경고] segment 상세 스텁을 못 찾음 — 수동 확인 필요")

if changed:
    p.write_text(s, encoding="utf-8")
PY

# ── 4) 테스트에 상세 mock 등록 ────────────────────────────────
python3 - << 'PY'
from pathlib import Path
p = Path("backend/tests/test_contract.py"); s = p.read_text(encoding="utf-8")
old = ('    "alerts_active.json": models.AlertsActiveResponse,\n'
       '    # "station_detail.json": models.StationDetail,   # ← 상세 mock 작업에서 추가\n'
       '    # "segment_detail.json": models.SegmentDetail,\n')
new = ('    "alerts_active.json": models.AlertsActiveResponse,\n'
       '    "station_detail.json": models.StationDetail,\n'
       '    "segment_detail.json": models.SegmentDetail,\n')
if old in s:
    p.write_text(s.replace(old, new), encoding="utf-8"); print("  test: 상세 mock 등록")
elif '"station_detail.json": models.StationDetail' in s:
    print("  test: 이미 등록됨(건너뜀)")
else:
    print("  [주의] 등록 지점을 못 찾음 — MOCK_MODEL_MAP 에 두 줄 수동 추가 필요")
PY

echo ">>> 완료. 다음:  (cd backend && pytest)   →  18 passed 예상"
