# 사용 기술 스택

`trail-dashboard`에서 실제로 사용한 기술 목록입니다. 버전은 `Dockerfile`·`docker-compose.yml`·`requirements*.txt`·`db/init_schema.sql` 기준이며, 버전을 고정하지 않은 항목은 "설치 시점 최신"입니다.

---

## 백엔드 · API

| 기술 | 버전 | 용도 |
|---|---|---|
| Python | 3.12 (`python:3.12-slim`) | 백엔드·파이프라인 런타임 |
| FastAPI | 최신 | 읽기 전용 REST API (CONTRACT §5) |
| Uvicorn (`uvicorn[standard]`) | 최신 | ASGI 서버 (`serve:app`, 포트 8000) |
| Pydantic | v2 이상 | 응답 모델 = 데이터 계약을 코드로 검증 |
| psycopg (`psycopg[binary]`) | 3 이상 | PostgreSQL 드라이버 (조회 전용) |
| python-dotenv | 최신 | `.env` 로드 |
| httpx | 0.27 이상 | LiteLLM 호출 클라이언트 · 테스트 클라이언트 |
| pypdf | 5 이상 | RAG 인제스트 시 PDF 문서 텍스트 추출 |

## 데이터 수집 · 집계 파이프라인 (`collector/` · `processor/`)

| 기술 | 용도 |
|---|---|
| pandas | 집계, CSV/엑셀 처리 (`vulnerability.py`, `delay.py`) |
| openpyxl | `pd.read_excel` 로 `.xlsx` 읽기 |
| requests | 코레일·기상청 공공 API 호출 |
| SQLAlchemy | `create_engine` 로 DB 읽기 (집계 단계) |

## 데이터베이스

| 기술 | 버전 | 용도 |
|---|---|---|
| PostgreSQL | 16 | 관계형 저장소 |
| TimescaleDB | `latest-pg16` | 시계열 하이퍼테이블 (`train_stops`, `weather_alerts`) |

> RAG 벡터 검색은 별도 벡터 DB(pgvector 등)를 쓰지 않습니다 — 아래 "RAG" 참고.

## RAG · LLM

| 기술 | 용도 |
|---|---|
| LiteLLM Proxy (`docker.litellm.ai/berriai/litellm:main-latest`) | 여러 LLM 공급자를 하나의 OpenAI 호환 API로 통일하는 모델 게이트웨이 (`litellm/config.yaml`) |
| Google Gemini (커밋 기본값) | 채팅·임베딩 모델. `.env` 의 `LITELLM_CHAT_MODEL`/`LITELLM_EMBED_MODEL` 로 교체 가능 |
| 파일 기반 JSON 인덱스 | RAG 인덱스를 Docker 볼륨(`/data/rag_index.json`)에 저장. 파일 수정 시각이 바뀌면 API가 자동 재로딩 (별도 벡터 DB 불필요) |
| 자체 경량 검색기 (`backend/rag/retriever.py`) | 임베딩 코사인 유사도 + 키워드 하이브리드, 권위(현재 구현 > 승인 문서 > 참고 문서) 가중 |

## 프론트엔드

| 기술 | 용도 |
|---|---|
| Vanilla JavaScript · HTML5 · CSS | 대시보드·역 상세·구간 상세 화면 (프레임워크 없음) |
| Lucide 아이콘 (SVG) | `frontend/assets/icons/` 에 개별 SVG로 포함 |
| 커스텀 렌더링 | 순위·히트맵·차트를 외부 차트/지도 라이브러리 없이 JS로 직접 그림 |

## 인프라 · 도구

| 기술 | 용도 |
|---|---|
| Docker · Docker Compose | 단일 이미지(`trail-dashboard-api`)로 API+정적 프론트. 서비스: `api` · `litellm` · `rag-ingest` · `db` (프로파일 `rag`/`db`로 분리) |
| Docker 볼륨 | `pgdata`(DB), `ragdata`(RAG 인덱스) |
| pytest | 응답 모델·정렬·표본 처리·RAG 대상 해석 등 자동화 테스트 |
| Git · GitHub | 협업 허브. GitHub Pages 로 mock 정적 호스팅 |

## 외부 데이터 출처

| 출처 | 데이터 |
|---|---|
| 기상청 API 허브 | 호우·폭염 기상특보 이력 및 현재 발효 현황 |
| 공공데이터포털 | 여객열차 운행계획·운행실적 (코레일·국토부) |

## 실행 모드

| 모드 | 설명 |
|---|---|
| `USE_MOCK=1` (기본) | DB 없이 `mock/*.json` 응답 — 프론트·API를 독립적으로 개발·검증 |
| `USE_MOCK=0` | TimescaleDB를 읽기 전용 조회. 두 모드가 **동일한 API 계약**을 사용 |
