# Gemini·LiteLLM API 키 발급 및 설정 가이드

## 1. 문서 목적

이 문서는 철도 취약구간 대시보드의 RAG 기능을 실행하기 위해 필요한 AI 관련 인증값을 발급하고 서버에 설정하는 방법을 설명한다.

현재 프로젝트에서 사용하는 구성은 다음과 같다.

- 답변 생성 모델: `gemini/gemini-3.5-flash`
- 임베딩 모델: `gemini/gemini-embedding-001`
- 모델 게이트웨이: LiteLLM Proxy
- 백엔드 → LiteLLM 주소: `http://litellm:4000/v1`

## 2. 핵심 개념

### 2.1 LiteLLM 전용 임베딩 API 키는 따로 발급하지 않는다

LiteLLM은 모델을 직접 제공하는 서비스가 아니라 Gemini 같은 외부 모델 제공자의 API를 공통 형식으로 호출하도록 중계하는 프록시다.

따라서 현재 구성에서는 Google에서 발급받은 `GEMINI_API_KEY` 하나를 다음 두 작업에 함께 사용한다.

- Gemini 채팅 모델 호출
- Gemini 임베딩 모델 호출

즉, 아래 두 모델에 별도의 Google API 키를 각각 발급할 필요는 없다.

```text
gemini/gemini-3.5-flash
gemini/gemini-embedding-001
```

### 2.2 LiteLLM Master Key는 직접 생성한다

`LITELLM_MASTER_KEY`는 Google에서 발급받는 키가 아니다. 이 키는 FastAPI 백엔드가 LiteLLM Proxy에 접근할 때 사용하는 내부 인증키다.

| 키 | 발급 또는 생성 주체 | 용도 |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio | LiteLLM이 Gemini 채팅·임베딩 API를 호출 |
| `LITELLM_MASTER_KEY` | 프로젝트 운영자 | LiteLLM Proxy 접근 보호 |
| `LITELLM_API_KEY` | 프로젝트 운영자 | 백엔드가 LiteLLM을 호출할 때 전달 |

현재 프로젝트에서는 `LITELLM_API_KEY`와 `LITELLM_MASTER_KEY`를 같은 값으로 사용할 수 있다.

### 2.3 답변 생성 모델: Gemini 3.5 Flash

현재 답변 생성에는 다음 LiteLLM 모델 문자열을 사용한다.

```text
gemini/gemini-3.5-flash
```

여기서 실제 Google Gemini 모델 ID는 `gemini-3.5-flash`이고, 앞의 `gemini/`는 LiteLLM이 Google Gemini 공급자를 식별하기 위해 붙이는 접두사다.

Gemini 3.5 Flash는 사용자 질문과 검색된 문서 근거를 입력받아 자연어 답변을 생성하는 대규모 언어 모델(LLM)이다. 현재 프로젝트에서는 다음 역할을 담당한다.

1. 사용자가 채팅 UI에 입력한 질문을 해석한다.
2. 현재 화면에서 전달된 철도 지표와 필터 정보를 참고한다.
3. RAG 검색으로 찾아온 설계서·기능명세서 등의 문서 조각을 참고한다.
4. 화면 데이터와 문서 근거를 종합해 한국어 답변을 생성한다.

프로젝트의 요청 흐름은 다음과 같다.

```text
사용자 질문
  → FastAPI /rag/ask
  → 관련 문서 검색
  → 화면 정보·라이브 지표·검색 근거 구성
  → LiteLLM Proxy
  → Gemini 3.5 Flash
  → 답변 반환
```

Gemini 3.5 Flash의 주요 특성은 다음과 같다.

| 항목 | 내용 |
|---|---|
| 모델 ID | `gemini-3.5-flash` |
| 프로젝트 설정값 | `gemini/gemini-3.5-flash` |
| 주된 역할 | 질문 해석, 근거 종합, 자연어 답변 생성 |
| 입력 | 텍스트, 이미지, 영상, 음성, PDF |
| 출력 | 텍스트 |
| 입력 한도 | 최대 1,048,576 토큰 |
| 출력 한도 | 최대 65,536 토큰 |
| 상태 | 안정화 버전 |
| 주요 기능 | Thinking, 구조화 출력, 함수 호출, 코드 실행, 캐싱 등 |

이 프로젝트에서는 긴 컨텍스트 전체를 무조건 전달하지 않고, RAG 검색 결과와 현재 화면에 필요한 데이터만 추려서 전달한다. 이렇게 하면 비용과 응답 시간을 줄이고, 관련 없는 정보가 답변에 섞이는 것을 줄일 수 있다.

### 2.4 임베딩 모델: Gemini Embedding 001

현재 문서 검색용 임베딩에는 다음 LiteLLM 모델 문자열을 사용한다.

```text
gemini/gemini-embedding-001
```

실제 Google Gemini 모델 ID는 `gemini-embedding-001`이며, 앞의 `gemini/`는 LiteLLM 공급자 접두사다.

임베딩 모델은 자연어 답변을 직접 생성하지 않는다. 텍스트를 의미를 나타내는 숫자 벡터로 변환한다. 의미가 비슷한 문장들은 벡터 공간에서도 가까운 위치에 배치되므로, 사용자의 질문과 가장 관련 있는 문서 조각을 찾는 데 사용할 수 있다.

현재 프로젝트에서는 다음 두 시점에 임베딩 모델을 사용한다.

#### 문서 등록 시

```text
PDF·Markdown 문서
  → 텍스트 추출
  → 작은 문서 조각으로 분할
  → 각 문서 조각을 임베딩 벡터로 변환
  → rag_index.json에 저장
```

#### 질문 처리 시

```text
사용자 질문
  → 질문을 임베딩 벡터로 변환
  → 저장된 문서 벡터와 유사도 비교
  → 가장 관련 있는 문서 조각 Top-K 선택
  → Gemini 3.5 Flash의 답변 근거로 전달
```

Gemini Embedding 001의 주요 특성은 다음과 같다.

| 항목 | 내용 |
|---|---|
| 모델 ID | `gemini-embedding-001` |
| 프로젝트 설정값 | `gemini/gemini-embedding-001` |
| 주된 역할 | 의미 기반 문서 검색과 유사도 계산 |
| 입력 | 텍스트 |
| 출력 | 텍스트 임베딩 벡터 |
| 입력 한도 | 최대 2,048 토큰 |
| 출력 차원 | 128~3072 |
| 권장 차원 | 768, 1536, 3072 |
| 상태 | 안정화 버전 |

출력 차원은 벡터 하나가 가지는 숫자의 개수다. 차원이 커지면 더 많은 의미 정보를 표현할 수 있지만 저장 공간과 계산량도 증가한다.

현재 구현처럼 출력 차원을 별도로 지정하지 않는 경우에는 API가 반환한 실제 벡터 길이를 기준으로 인덱스를 생성한다. 임베딩 모델이나 출력 차원을 변경하면 기존 문서 벡터와 새 질문 벡터의 형식이 달라질 수 있으므로 반드시 RAG 인덱스를 다시 생성해야 한다.

### 2.5 두 모델이 모두 필요한 이유

두 모델은 서로 다른 역할을 수행한다.

| 구분 | Gemini 3.5 Flash | Gemini Embedding 001 |
|---|---|---|
| 역할 | 답변 생성 | 관련 문서 검색 |
| 결과 형태 | 자연어 문장 | 숫자 벡터 |
| 사용 시점 | 사용자가 질문할 때 | 문서 등록 및 질문 검색 시 |
| 직접 사용자에게 표시 | 표시됨 | 표시되지 않음 |

임베딩 모델 없이 LLM만 사용하면 프로젝트 문서 중 어떤 내용을 참고해야 하는지 효율적으로 찾기 어렵다. 반대로 임베딩 모델만 사용하면 관련 문서는 찾을 수 있지만 자연어 답변을 만들 수 없다.

따라서 현재 RAG 구조는 다음과 같이 결합한다.

```text
Gemini Embedding 001
  → 질문과 관련된 문서 검색

Gemini 3.5 Flash
  → 검색된 문서와 화면 데이터를 바탕으로 최종 답변 생성
```

---


## 3. Gemini API 키 발급

### 3.1 Google AI Studio에서 생성

1. Google 계정으로 Google AI Studio에 로그인한다.
2. **API Keys** 메뉴로 이동한다.
3. 신규 사용자는 기본 프로젝트와 API 키가 자동 생성되어 있을 수 있다.
4. 새 키가 필요하면 **Create API key**를 선택한다.
5. 기존 Google Cloud 프로젝트를 선택하거나 새 프로젝트를 만든다.
6. 생성된 API 키를 복사한다.

복사한 키는 다음 환경 변수로 사용한다.

```dotenv
GEMINI_API_KEY=발급받은_키
```

### 3.2 키 유형 확인

2026년 기준 Google AI Studio에서 새로 생성되는 키는 기본적으로 인증 키(Auth Key)다.

기존 표준 키(Standard Key)를 사용 중이라면 새 인증 키로 교체하는 것이 안전하다. Google은 2026년 9월부터 표준 키 요청을 거부할 예정이므로 기존 키를 계속 사용하는 환경은 그 전에 교체해야 한다.

### 3.3 유료 등급 설정

무료 등급만으로 개발 테스트가 가능할 수 있으나 다음 상황에서는 결제 설정이 필요할 수 있다.

- 무료 호출 한도 초과
- 팀 단위 반복 테스트
- 많은 문서 임베딩
- 운영 환경에서 지속적인 채팅 요청
- 더 높은 요청 속도 제한이 필요한 경우

Google AI Studio의 API Keys 또는 Projects 화면에서 **Set up billing**을 선택해 Cloud Billing을 연결한다.

---

## 4. LiteLLM Master Key 생성

`LITELLM_MASTER_KEY`는 외부 사이트에서 발급받는 키가 아니라 프로젝트 운영자가 직접 생성하는 내부 인증키다. 운영체제에 따라 아래 방법 중 하나를 사용한다.

### 4.1 Linux 또는 macOS

OpenSSL이 설치되어 있다면 다음 명령으로 32바이트 무작위 값을 생성한다.

```bash
openssl rand -hex 32
```

출력값 앞에 `sk-litellm-` 접두사를 붙여 사용한다.

```dotenv
LITELLM_MASTER_KEY=sk-litellm-생성한_무작위값
LITELLM_API_KEY=sk-litellm-생성한_무작위값
```

한 번에 접두사까지 출력하려면 다음처럼 실행할 수 있다.

```bash
printf 'sk-litellm-'
openssl rand -hex 32
```

### 4.2 Windows PowerShell

Windows PowerShell 5.1과 PowerShell 7에서 모두 사용할 수 있는 방법이다.

```powershell
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()

$key = "sk-litellm-" + (($bytes | ForEach-Object {
    $_.ToString("x2")
}) -join "")

$key
```

출력 예시:

```text
sk-litellm-9a83f20d4d...생략...7c2b
```

출력된 값을 `.env`의 두 항목에 동일하게 넣는다.

```dotenv
LITELLM_MASTER_KEY=sk-litellm-생성된_값
LITELLM_API_KEY=sk-litellm-생성된_값
```

PowerShell에서 `.env` 파일을 메모장으로 열려면 프로젝트 폴더에서 다음 명령을 실행한다.

```powershell
notepad .env
```

### 4.3 Windows에서 Python 사용

Python이 설치되어 있다면 PowerShell 또는 명령 프롬프트에서 다음 명령을 사용할 수 있다.

```powershell
python -c "import secrets; print('sk-litellm-' + secrets.token_hex(32))"
```

`python` 명령이 인식되지 않고 Python Launcher가 설치되어 있다면 다음처럼 실행한다.

```powershell
py -c "import secrets; print('sk-litellm-' + secrets.token_hex(32))"
```

### 4.4 Windows Git Bash에서 OpenSSL 사용

Git for Windows의 Git Bash 환경에 OpenSSL이 포함되어 있다면 Linux와 같은 방식으로 생성할 수 있다.

```bash
printf 'sk-litellm-'
openssl rand -hex 32
```

### 4.5 환경 변수의 역할

두 환경 변수에는 같은 값을 넣는다.

- `LITELLM_MASTER_KEY`: LiteLLM Proxy가 검증하는 키
- `LITELLM_API_KEY`: FastAPI 백엔드가 LiteLLM 요청에 넣는 키

키를 생성할 때는 다음 조건을 지킨다.

- 32바이트 이상의 암호학적으로 안전한 난수를 사용한다.
- 사람이 직접 만든 단어나 날짜, 프로젝트명은 사용하지 않는다.
- 운영 환경과 개발 환경에서 서로 다른 키를 사용한다.
- 키를 GitHub, 메신저, 문서 캡처에 노출하지 않는다.

---

## 5. 프로젝트 `.env` 설정

프로젝트 루트의 `.env`에 다음 값을 설정한다.

```dotenv
# Google Gemini 공급자 키
GEMINI_API_KEY=여기에_Google_AI_Studio_키

# LiteLLM Proxy 내부 인증키
LITELLM_MASTER_KEY=sk-litellm-충분히_긴_무작위값
LITELLM_API_KEY=sk-litellm-충분히_긴_무작위값

# LiteLLM이 실제로 호출할 Google 모델
LITELLM_CHAT_MODEL=gemini/gemini-3.5-flash
LITELLM_EMBED_MODEL=gemini/gemini-embedding-001

# FastAPI가 호출할 LiteLLM 주소
LITELLM_BASE_URL=http://litellm:4000/v1

# FastAPI가 사용하는 LiteLLM 모델 별칭
RAG_CHAT_MODEL=rag-chat
RAG_EMBED_MODEL=rag-embedding

# RAG 설정
RAG_ENABLED=1
RAG_COLLECTION=project
RAG_INDEX_FILE=/data/rag_index.json
RAG_TOP_K=5
RAG_REQUEST_TIMEOUT=180
RAG_EMBED_BATCH_SIZE=16
```

### 주의

실제 키를 다음 파일에 넣지 않는다.

```text
.env.example
README.md
docker-compose.yml
litellm/config.yaml
frontend/*.js
```

실제 키는 `.env`에만 보관하고 `.env`는 Git에 커밋하지 않는다.

---

## 6. LiteLLM 모델 설정

`litellm/config.yaml`은 다음처럼 구성한다.

```yaml
model_list:
  - model_name: rag-chat
    litellm_params:
      model: os.environ/LITELLM_CHAT_MODEL
      api_key: os.environ/GEMINI_API_KEY

  - model_name: rag-embedding
    litellm_params:
      model: os.environ/LITELLM_EMBED_MODEL
      api_key: os.environ/GEMINI_API_KEY

litellm_settings:
  drop_params: true

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  disable_spend_logs: true
  disable_spend_updates: true
```

중요한 점은 채팅과 임베딩 모델 모두 같은 `GEMINI_API_KEY`를 사용한다는 것이다.

---

## 7. Docker Compose 환경 설정

LiteLLM 서비스에는 필요한 변수만 전달하는 것이 안전하다.

```yaml
litellm:
  image: docker.litellm.ai/berriai/litellm:main-latest
  profiles: ["rag"]
  command:
    - "--config"
    - "/app/config.yaml"
    - "--port"
    - "4000"

  environment:
    GEMINI_API_KEY: "${GEMINI_API_KEY}"
    LITELLM_MASTER_KEY: "${LITELLM_MASTER_KEY}"
    LITELLM_CHAT_MODEL: "${LITELLM_CHAT_MODEL:-gemini/gemini-3.5-flash}"
    LITELLM_EMBED_MODEL: "${LITELLM_EMBED_MODEL:-gemini/gemini-embedding-001}"

  volumes:
    - ./litellm/config.yaml:/app/config.yaml:ro

  ports:
    - "127.0.0.1:4000:4000"

  restart: unless-stopped
```

`127.0.0.1:4000`으로 바인딩하면 외부 네트워크에서 LiteLLM Proxy 포트에 직접 접근하는 것을 막을 수 있다.

---

## 8. 서비스 실행

```bash
docker compose --profile rag up -d litellm
```

로그 확인:

```bash
docker compose logs --tail=100 litellm
```

정상 시작 예시:

```text
Application startup complete
Uvicorn running on http://0.0.0.0:4000
Proxy initialized with Config
rag-chat
rag-embedding
```

---

## 9. 채팅 모델 연결 테스트

```bash
curl -sS http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rag-chat",
    "messages": [
      {
        "role": "user",
        "content": "연결 성공이라고만 답해"
      }
    ]
  }' |
python -m json.tool --no-ensure-ascii
```

응답의 `choices[0].message.content`에 답변이 들어 있으면 정상이다.

---

## 10. 임베딩 모델 연결 테스트

```bash
curl -sS http://127.0.0.1:4000/v1/embeddings \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rag-embedding",
    "input": [
      "철도 지연과 기상특보의 관계"
    ]
  }' |
python -m json.tool
```

정상 응답에는 다음 구조가 포함된다.

```json
{
  "data": [
    {
      "embedding": [0.01, -0.02, 0.03]
    }
  ]
}
```

실제 임베딩 벡터는 훨씬 길다. `gemini-embedding-001`은 128~3072 차원을 지원한다.

---

## 11. RAG 인덱스 다시 생성

Gemini API 키를 새로 설정했거나 임베딩 모델을 변경한 경우 기존 인덱스를 삭제하고 다시 생성한다.

```bash
docker compose --profile rag run --rm \
  --entrypoint sh api \
  -c 'rm -f /data/rag_index.json'
```

```bash
docker compose --profile rag run --rm rag-ingest
```

생성 확인:

```bash
docker compose --profile rag run --rm \
  --entrypoint sh api \
  -c 'ls -lh /data/rag_index.json'
```

---

## 12. FastAPI RAG 상태 확인

```bash
docker compose --profile rag up -d --build api
```

```bash
curl -sS http://127.0.0.1:8000/rag/health |
python -m json.tool --no-ensure-ascii
```

확인 항목:

```text
enabled: true
index_ready: true
chat_model: rag-chat
embedding_model: rag-embedding
document_count: 1 이상
chunk_count: 1 이상
```

---

## 13. 자주 발생하는 오류

### 13.1 Gemini 인증 오류

증상:

```text
401
API key not valid
Permission denied
```

키 전체를 출력하지 않고 설정 여부만 확인한다.

```bash
docker compose exec litellm sh -c '
python - <<PY
import os
key = os.getenv("GEMINI_API_KEY", "")
print("설정 여부:", bool(key))
print("길이:", len(key))
PY
'
```

### 13.2 LiteLLM 인증 오류

증상:

```text
401 Unauthorized
Invalid proxy server token
```

원인:

```text
LITELLM_API_KEY와 LITELLM_MASTER_KEY가 다름
```

확인:

```bash
grep -E '^LITELLM_(API|MASTER)_KEY=' .env
```

두 값이 동일해야 한다.

### 13.3 모델을 찾지 못함

증상:

```text
model not found
invalid model
```

확인:

```dotenv
LITELLM_CHAT_MODEL=gemini/gemini-3.5-flash
LITELLM_EMBED_MODEL=gemini/gemini-embedding-001
```

```yaml
model_name: rag-chat
model_name: rag-embedding
```

애플리케이션은 Google 모델명을 직접 호출하지 않고 LiteLLM 별칭을 호출한다.

### 13.4 호출 한도 초과

증상:

```text
429 Too Many Requests
Rate limit exceeded
Resource exhausted
```

대응:

- 잠시 후 재시도
- 임베딩 배치 크기 축소
- 무료 사용량 확인
- 유료 등급 전환 검토
- 중복 인덱싱 방지

---

## 14. 보안 수칙

1. Gemini API 키를 프론트엔드 JavaScript에 넣지 않는다.
2. Gemini API 키를 GitHub에 커밋하지 않는다.
3. `.env`가 `.gitignore`에 포함되어 있는지 확인한다.
4. 채팅 UI는 FastAPI의 `/rag/ask`만 호출한다.
5. 브라우저가 LiteLLM 4000번 포트를 직접 호출하지 않도록 한다.
6. LiteLLM 4000번 포트는 `127.0.0.1` 또는 내부 Docker 네트워크로만 노출한다.
7. 키가 노출되면 즉시 Google AI Studio에서 폐기하고 새 키를 발급한다.
8. 키 교체 후 LiteLLM 컨테이너를 다시 생성한다.
9. 운영용과 개발용 Google 프로젝트 및 키를 분리하는 것이 좋다.
10. 실제 키를 메신저나 공개 문서로 공유하지 않는다.

---
