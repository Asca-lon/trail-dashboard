# QUICKSTART — clone 후 바로 실행

`git clone` 하고 **명령 한 줄**이면 대시보드·API가 뜬다. Python 설치도, 가상환경도, 패키지 설치도 필요 없다 — 전부 컨테이너 안에서 처리된다. RAG(문서·지표 근거 설명)는 API 키가 필요한 선택 단계다(아래 2·3단계).

> 도커 자체 설치(Windows/macOS/Linux)는 [`Docker_run.md`](./Docker_run.md), 서버에 SSH로 직접 띄우는 방법은 [`server_RUN.md`](./server_RUN.md)를 본다. 이 문서는 **자기 PC에서 clone → 실행**만 다룬다. 응답 계약의 단일 원천은 [`CONTRACT.md`](./CONTRACT.md).

---

## 0. 준비물 (최초 1회)

| 필요한 것 | 확인 |
|---|---|
| **Git** | `git --version` |
| **Docker** (`docker compose`) | `docker --version` 과 `docker compose version` |

Windows/macOS는 **Docker Desktop 앱을 먼저 켜고** 고래 아이콘이 멈출 때까지 기다린다. 없으면 [`Docker_run.md`](./Docker_run.md)의 설치 안내로 먼저 간다.

---

## 1. 클론하고 실행 (mock, 키 불필요)

```bash
git clone https://github.com/Asca-lon/trail-dashboard.git
cd trail-dashboard
docker compose up
```

처음엔 이미지를 빌드하느라 몇 분 걸린다. 로그가 잦아들면 준비 완료다. 브라우저에서:

- 대시보드 → **http://localhost:8000**
- API 문서(Swagger) → http://localhost:8000/docs
- 헬스체크 → http://localhost:8000/health  (`{"status":"ok","mode":"mock"}`)

끝낼 때는 실행 중인 터미널에서 `Ctrl+C`, 또는 다른 터미널에서 `docker compose down`.

> 이 단계는 **mock 모드**다. A의 DB 없이 `mock/*.json` 값으로 화면이 그대로 돈다.
> 화면의 AI 채팅 드로어도 이 단계에선 예시 응답(Mock UI)만 보여주고, `/rag/ask` 는
> RAG가 꺼져 있다(503)고 안내한다. 실제 RAG 답변은 2단계부터.

---

## 2. (선택) RAG 실제 답변 켜기 — API 키 + `--profile rag`

RAG 채팅이 문서·코드·지표를 근거로 진짜 답을 하게 하려면 LLM 키와 `rag` 프로파일이 필요하다.

**(a) `.env` 만들고 키 채우기**

```bash
cp .env.example .env
# .env 를 열어 아래 값을 채운다
```

```dotenv
GEMINI_API_KEY=발급받은_Gemini_키
LITELLM_MASTER_KEY=충분히_긴_임의의_키
LITELLM_API_KEY=위와_같은_값
# RAG_ENABLED=1 은 .env.example 에 이미 들어 있다
```

**(b) RAG 스택 띄우기 (mock 지표 위에서)**

```bash
USE_MOCK=1 docker compose --profile rag up -d --build
```

> ⚠️ 앞에 `USE_MOCK=1` 을 붙이는 이유: `.env.example` 은 `USE_MOCK=0` 이라, 그대로 두면
> api 가 DB 모드로 떠서 (아직 없는) DB 를 찾다 화면이 깨진다. mock 위에서 RAG 만 시험할
> 땐 명령에서 `USE_MOCK=1` 로 덮어쓴다. (항상 mock 이 편하면 `.env` 의 `USE_MOCK` 을 1 로.)

litellm 이 잘 떴는지 로그로 확인:

```bash
docker compose logs --tail=50 litellm
```

**(c) 인덱스 만들기 — 최초 1회**

RAG는 프로젝트 문서·소스코드를 한 번 인제스트해 검색 인덱스를 만든 뒤 동작한다. 1회성 작업이라 별도로 실행한다:

```bash
docker compose --profile rag run --rm rag-ingest
```

> 인덱스가 없으면 `/rag/ask` 는 503(`RAG_INDEX_NOT_READY`)로 "먼저 인제스트하라"고 안내한다.

**(d) 확인**

```bash
curl -sS http://localhost:8000/rag/health

curl -sS -X POST http://localhost:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"역 취약도는 어떤 기준으로 계산돼?"}'
```

한 번에 점검하려면: `bash scripts/rag_smoke_test.sh`

---

## 3. (선택) 실제 DB로 보기

기본은 mock 모드다. A가 채운 집계 DB를 읽으려면 DB 컨테이너까지 함께 띄운다:

```bash
USE_MOCK=0 docker compose --profile db up
```

- `db/init_schema.sql` 이 최초 1회 실행되어 빈 스키마가 만들어진다.
- **집계 데이터 적재는 A의 collector/processor 몫**이라 이 compose 범위 밖이다. 수집기를 돌리려면 `.env` 에 `PUBLIC_DATA_API_KEY`·`KMA_API_KEY` 도 채운다.
- **RAG + DB 를 동시에** 쓰려면 두 프로파일을 같이 준다:

```bash
USE_MOCK=0 docker compose --profile rag --profile db up -d --build
```

---

## 실행 조합 한눈에

| 하고 싶은 것 | 명령 |
|---|---|
| 대시보드+API (mock, 키 불필요) | `docker compose up` |
| RAG 스택 (mock 지표 위) | `USE_MOCK=1 docker compose --profile rag up -d --build` |
| RAG 인덱스 최초 생성 | `docker compose --profile rag run --rm rag-ingest` |
| 실제 DB | `USE_MOCK=0 docker compose --profile db up` |
| RAG + 실제 DB | `USE_MOCK=0 docker compose --profile rag --profile db up -d --build` |
| 코드 바꾼 뒤 다시 빌드 | 위 명령에 `--build` 추가 |
| 백그라운드 실행 / 종료 | `... up -d` / `docker compose down` |
| 로그 보기 | `docker compose logs -f api` (또는 `litellm`) |

---

## 막힐 때

| 증상 | 원인·조치 |
|---|---|
| `cannot find ... dockerDesktopLinuxEngine` | Docker Desktop 앱이 안 켜져 있다. 앱 실행 후 고래가 멈추면 재시도. |
| `port is already allocated` (8000) | 다른 프로그램이 8000을 쓰는 중. 그 프로그램을 끄거나, compose 의 `ports` 를 `"8080:8000"` 처럼 바꾼다. |
| `.env` 만든 뒤 `docker compose up` 하니 화면이 깨짐 | `.env.example` 이 `USE_MOCK=0` 이라 DB 모드로 떴는데 db 가 없어서다. `USE_MOCK=1 docker compose up` 으로 띄우거나 `.env` 의 `USE_MOCK` 을 1 로. |
| 화면은 뜨는데 AI 채팅이 예시만 답함 | 1단계(mock)에선 정상. 실제 답변은 2단계(키+`--profile rag`+인덱스)를 거쳐야 한다. |
| `/rag/ask` 가 503 (`RAG_DISABLED`) | `.env` 의 `RAG_ENABLED=1` 확인. `.env` 없이 띄우면 RAG 가 꺼져 있다. |
| `/rag/ask` 가 503 (`RAG_INDEX_NOT_READY`) | 인덱스가 없다. `docker compose --profile rag run --rm rag-ingest` 먼저. |
| `/rag/ask` 가 502 (`LITELLM_ERROR`) | litellm 은 떴지만 모델 호출 실패. `.env` 의 `GEMINI_API_KEY` 와 `LITELLM_CHAT_MODEL`/`LITELLM_EMBED_MODEL` 의 모델명이 실제 존재하는지 확인. |
| 역/구간 카드가 전부 `-` | mock 모드에선 정상 범위. 실제 값은 DB 모드(3단계)에서 나온다. |
