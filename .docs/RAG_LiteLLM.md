# RAG + LiteLLM 서버 실행

## 구성

```text
curl / frontend
    → FastAPI POST /rag/ask
        ├─ target_resolver: 질문의 역·구간 판별
        ├─ 기존 get_stations/get_segments: 대시보드와 동일한 현재 지표
        ├─ /data/rag_index.json: 프로젝트 문서·코드 검색
        └─ LiteLLM Proxy
             ├─ rag-chat      → AI 채팅 모델
             └─ rag-embedding → AI 임베딩 모델
```

MVP 인덱스는 Docker named volume `ragdata`의 JSON 파일로 저장한다. 철도 시계열 DB와 분리되어 있어 기존 TimescaleDB 이미지와 스키마를 변경하지 않는다.

## 1. 환경 파일

```bash
cp .env.example .env
```

최소 수정 항목:

```dotenv
RAG_ENABLED=1
OPENAI_API_KEY=sk-...
LITELLM_MASTER_KEY=충분히_긴_임의의_키
LITELLM_API_KEY=위와_같은_값
```

기본 모델:

```dotenv
LITELLM_CHAT_MODEL=openai/gpt-5-mini
LITELLM_EMBED_MODEL=openai/text-embedding-3-small
```

모델을 변경하면 `rag-ingest`를 다시 실행해야 한다. 문서와 질문은 반드시 같은 임베딩 모델을 사용한다.

## 2. 이미지 빌드와 서비스 시작

mock 지표로 먼저 확인:

```bash
USE_MOCK=1 docker compose --profile rag up -d --build api litellm
```

실제 TimescaleDB까지 함께 시작:

```bash
USE_MOCK=0 docker compose --profile rag --profile db up -d --build api litellm db
```

상태 확인:

```bash
docker compose ps
docker compose logs --tail=100 litellm
docker compose logs --tail=100 api
```

## 3. LiteLLM 자체 연결 확인

```bash
curl -sS http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"rag-chat",
    "messages":[{"role":"user","content":"연결 확인이라고 한 문장으로 답해줘"}]
  }'
```

임베딩 확인:

```bash
curl -sS http://127.0.0.1:4000/v1/embeddings \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"rag-embedding","input":["역 취약도 계산 기준"]}'
```

## 4. 프로젝트 인제스트

LiteLLM이 정상인 상태에서 1회 실행한다.

```bash
docker compose --profile rag run --rm rag-ingest
```

소스 코드나 계약 문서가 바뀌면 같은 명령을 다시 실행한다. 파일은 원자적으로 교체되며 API는 수정 시각을 감지해 자동으로 새 인덱스를 읽는다.

RAG 상태 확인:

```bash
curl -sS http://127.0.0.1:8000/rag/health
```

정상 예:

```json
{
  "enabled": true,
  "index_ready": true,
  "collection": "project",
  "chat_model": "rag-chat",
  "embedding_model": "rag-embedding",
  "document_count": 60,
  "chunk_count": 1200,
  "git_commit": "abc1234"
}
```

## 5. 채팅 curl 테스트

문서 설명:

```bash
curl -sS -X POST http://127.0.0.1:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"역 취약도는 어떤 기준으로 계산돼?"}'
```

역 지표와 문서 결합:

```bash
curl -sS -X POST http://127.0.0.1:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"대전역은 왜 이 등급이야?"}'
```

상세 화면 context 우선:

```bash
curl -sS -X POST http://127.0.0.1:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question":"이 구간이 왜 취약한지 설명해줘",
    "context": {
      "target_type":"segment",
      "target_id":"daejeon-gimcheon_gumi"
    }
  }'
```

## 6. 프론트엔드 연결 계약

프론트엔드는 같은 origin의 `/rag/ask`만 호출하면 된다.

```javascript
const response = await fetch("/rag/ask", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question,
    context: selectedTarget
      ? {
          target_type: selectedTarget.type,
          target_id: selectedTarget.id,
        }
      : null,
  }),
});

const data = await response.json();
```

렌더링 기준:

- `answer`: 채팅 본문
- `targets`: 대시보드 원값과 등급 표시
- `sources`: 파일·섹션·PDF 페이지 출처
- `limitations`: 표본 부족, 비인접 구간 등 안내
- `resolution`: context/text_match/none 디버깅 정보

프론트는 LLM 본문에 있는 숫자를 다시 파싱하지 않고 `targets[].metrics`를 직접 표시한다.

## 7. 운영 주의사항

- 서버 방화벽에서 4000번 포트를 외부에 공개하지 않는다. Compose는 기본적으로 `127.0.0.1`에만 바인딩한다.
- `.env`와 API 키를 커밋하지 않는다.
- `LITELLM_MASTER_KEY` 기본값은 개발 전용이므로 서버에서 반드시 교체한다.
- LiteLLM 이미지는 검증 후 특정 버전 또는 digest로 고정하는 것이 좋다.
- 현재 인덱스는 파일 기반 MVP다. 문서 규모와 동시 사용자가 증가하면 pgvector 저장소로 교체한다.
