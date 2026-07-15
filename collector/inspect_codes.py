"""
collector/inspect_codes.py — seed_stations.sql 을 만들기 위한 '실제 코드' 조회.

실행:
  docker compose exec api python -u collector/inspect_codes.py

  ※ -u 를 붙이면 출력이 즉시 보인다(버퍼링 방지).

왜 필요한가:
  지금 세 코드 체계가 섞여 있어 취약도 집계가 0행이 된다.
    - weather_alerts.region_code : 'L1020800' (특보구역)  ← wrn_met_data.php 가 주는 값
    - seed_stations.sql          : '11C20401' (예보구역)  ← 매칭 안 됨
    - update_stations.py         : '133'      (지점번호)  ← 매칭 안 됨
  vulnerability.py 는 stations.region_code == weather_alerts.region_code 로 매칭한다.
  따라서 stations.region_code 는 반드시 **특보구역(L형식)** 이어야 한다.
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

PUBLIC_API_KEY = os.getenv("PUBLIC_DATA_API_KEY")
KMA_API_KEY = os.getenv("KMA_API_KEY")
KORAIL_RUN_API_URL = os.getenv("KORail_RUN_API_URL", "https://apis.data.go.kr/B551457/run/v2")
KMA_WRN_REG_URL = os.getenv("KMA_WRN_REG_URL", "https://apihub.kma.go.kr/api/typ01/url/wrn_reg.php")

# 경부고속선(KTX) 10개 역. API 표기가 다를 수 있어 후보를 넉넉히 둔다.
WANT = ["서울", "광명", "천안아산", "천안", "오송", "대전",
        "김천구미", "김천(구미)", "김천", "동대구", "경주", "신경주",
        "울산", "울산(통도사)", "부산"]

MAX_PAGES = int(os.getenv("INSPECT_MAX_PAGES", "30"))


def find_station_codes(run_ymd="20260714"):
    print("=" * 70, flush=True)
    print("1) 코레일 역코드 → stations.station_code 에 넣을 값", flush=True)
    print("=" * 70, flush=True)

    if not PUBLIC_API_KEY:
        print("❌ PUBLIC_DATA_API_KEY 없음 (.env / env_file 확인)", flush=True)
        return

    url = f"{KORAIL_RUN_API_URL}/travelerTrainRunInfo2"
    found = {}
    all_names = set()

    for page_no in range(1, MAX_PAGES + 1):
        params = {
            "serviceKey": requests.utils.unquote(PUBLIC_API_KEY),
            "pageNo": str(page_no), "numOfRows": "1000",
            "runYmd": run_ymd, "_type": "json",
        }
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code != 200:
                print(f"  ❌ HTTP {r.status_code} — 중단", flush=True)
                break

            body = r.json().get("response", {}).get("body", {})
            items = body.get("items", {}).get("item", [])
            if isinstance(items, dict):
                items = [items]
            if not items:
                print(f"  page {page_no}: 항목 없음 — 종료", flush=True)
                break

            # 첫 페이지에서 실제 필드 이름·역명 표기를 보여준다(진단용).
            if page_no == 1:
                print(f"  [진단] 첫 항목의 키: {sorted(items[0].keys())}", flush=True)
                print(f"  [진단] 첫 항목 샘플: {items[0]}", flush=True)
                print(f"  [진단] totalCount: {body.get('totalCount')}", flush=True)
                print("", flush=True)

            for it in items:
                nm = str(it.get("stn_nm") or it.get("stnNm") or "").strip()
                cd = str(it.get("stn_cd") or it.get("stnCd") or "").strip()
                if not nm:
                    continue
                all_names.add(nm)
                if nm in WANT and nm not in found:
                    found[nm] = cd
                    print(f"  ✅ 발견: {nm:12s} → {cd}", flush=True)

            print(f"  page {page_no} 처리 완료 (누적 발견 {len(found)}/{len(WANT)}, "
                  f"전체 역명 {len(all_names)}종)", flush=True)

            total = body.get("totalCount", 0)
            try:
                total = int(total)
            except (TypeError, ValueError):
                total = 0
            if total and page_no * 1000 >= total:
                print("  (마지막 페이지 도달)", flush=True)
                break

        except Exception as e:
            print(f"  ❌ page {page_no} 오류: {e}", flush=True)
            break

    print("", flush=True)
    print("  ── 결과 ──", flush=True)
    for nm in WANT:
        if nm in found:
            print(f"  {nm:12s} → {found[nm]}", flush=True)
    missing = [n for n in WANT if n not in found]
    if missing:
        print(f"  ⚠️ 못 찾음: {missing}", flush=True)
        # 이름 표기가 다를 수 있으니 비슷한 후보를 보여준다.
        hints = sorted(n for n in all_names
                       if any(k in n for k in ["서울", "광명", "천안", "아산", "오송",
                                               "대전", "김천", "구미", "대구", "경주",
                                               "울산", "부산"]))
        print(f"  💡 API 가 준 유사 역명: {hints}", flush=True)
    print("", flush=True)


def list_warning_regions():
    print("=" * 70, flush=True)
    print("2) 기상청 특보구역 코드 → stations.region_code 에 넣을 값", flush=True)
    print("=" * 70, flush=True)

    if not KMA_API_KEY:
        print("❌ KMA_API_KEY 없음", flush=True)
        return
    try:
        r = requests.get(KMA_WRN_REG_URL, params={"authKey": KMA_API_KEY}, timeout=20)
        print(f"  HTTP {r.status_code}, {len(r.text)} bytes", flush=True)
        for enc in ("euc-kr", "utf-8"):
            try:
                r.encoding = enc
                text = r.text
                if "�" not in text[:500]:
                    break
            except Exception:
                continue

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        print(f"  총 {len(lines)}줄", flush=True)
        print("  ── 원문 앞 10줄(형식 확인) ──", flush=True)
        for l in lines[:10]:
            print("   ", l, flush=True)
        print("", flush=True)

        keywords = ["서울", "광명", "아산", "천안", "청주", "오송", "대전",
                    "김천", "구미", "대구", "경주", "울산", "부산"]
        hit = [l for l in lines if not l.startswith("#") and any(k in l for k in keywords)]
        print(f"  ── 우리 역 관련 {len(hit)}줄 ──", flush=True)
        for l in hit[:80]:
            print("   ", l, flush=True)

    except Exception as e:
        print(f"  ❌ 오류: {e}", flush=True)
    print("", flush=True)


if __name__ == "__main__":
    print(f"[시작] PUBLIC_DATA_API_KEY={'O' if PUBLIC_API_KEY else 'X'}, "
          f"KMA_API_KEY={'O' if KMA_API_KEY else 'X'}", flush=True)
    print("", flush=True)
    find_station_codes()
    list_warning_regions()
    print("위 두 결과를 복사해서 알려주면 seed_stations.sql 을 만듭니다.", flush=True)
