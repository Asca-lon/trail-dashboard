# 경부선 기상 취약구간 사전 점검 대시보드

철도 관리자가 이상기후(호우·폭염) 특보 시 **취약한 역·구간**을 사전 점검하도록 돕는 대시보드.
실시간 관제가 아니라 **사전 점검·대비용**. 경부선만 구현하되 다노선 확장 구조.

> **단일 진실 원천은 [`CONTRACT.md`](./CONTRACT.md).** 다른 문서와 어긋나면 CONTRACT 가 우선한다.

## 폴더

| 폴더 | 담당 | 내용 |
|---|---|---|
| `db/` `collector/` `processor/` | A | 스키마·적재, 수집(운행계획·운행정보·특보), 지연 계산·취약도 집계 |
| `backend/` | B | 읽기 전용 API (FastAPI). CONTRACT §5 를 그대로 노출 |
| `frontend/` | C | 대시보드(순위표·히트맵·상세) |
| `mock/` | 공유 | CONTRACT §5 모양의 mock JSON. **협업의 핵심** |
| `index.html` | B | GitHub Pages 콘솔 — mock 을 안정 URL 로 호스팅 + 살아있는 API 문서 |

## GitHub Pages (mock 호스팅)

Settings → Pages → Source: `main` 브랜치 `/ (root)` 로 배포하면:

- 콘솔: `https://<계정>.github.io/<레포>/`
- mock: `https://<계정>.github.io/<레포>/mock/vulnerability_segments.json`

C는 이 URL 로 화면을 만들고, 백엔드 완성 후 **base URL 만 교체**한다(파싱 코드는 그대로 — 계약이 지켜지면 그래야 한다).

## 백엔드 실행

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env      # USE_MOCK=1 로 시작
uvicorn api:app --reload --port 8000
```

- 문서: http://localhost:8000/docs
- `USE_MOCK=1` (기본): A의 DB 없이 `mock/*.json` 으로 응답 → 오늘 바로 워킹 스켈레톤.
- `USE_MOCK=0`: A가 채운 TimescaleDB 를 **읽기 전용**으로 조회. 두 모드 모두 **같은 계약 모양**이라 C는 전환을 못 느낀다.

## 계약 요점 (§5-1)

- 키는 항상 존재. 빈 값은 `[]`/`null` (에러 아님). 표본 0 = `200 + []`, 오류만 `4xx/5xx`.
- 순위는 취약도 내림차순 정렬해서 내려준다.
- 단위 고정: 지연 = 분, 비율(delay_rate·stop_rate·vuln) = 0~1.
- 필터 허용값: `alert_type`(대설/호우/폭염/강풍/태풍/한파), `alert_level`(주의보/경보), `train_type`(all/KTX/무궁화/새마을), `line`.
- 에러 형식 통일: `{ "error": { "code", "message" } }`
