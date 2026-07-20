# trail-dashboard RAG + LiteLLM 적용 번들

기준 저장소: `Asca-lon/trail-dashboard`
확인 기준 main HEAD: `fac52dfa1f98600f625f32bf05d1c9fe4dbc2b8f`

## 1. 로컬 또는 서버 저장소에서 패치 적용

작업물이 있으면 먼저 커밋하거나 stash 합니다.

```bash
cd /srv/trail-dashboard   # 실제 clone 경로로 변경
git status
git pull --ff-only origin main

git apply --check /path/to/trail-dashboard-rag-litellm.patch
git apply /path/to/trail-dashboard-rag-litellm.patch
```

검사:

```bash
python -m compileall -q backend/rag
cd backend && pytest -q tests/test_rag_target_resolver.py tests/test_rag_retriever.py
cd ..
```

## 2. 환경변수

```bash
cp .env.example .env
nano .env
```

반드시 설정:

```dotenv
RAG_ENABLED=1
OPENAI_API_KEY=sk-실제_API_키
LITELLM_MASTER_KEY=충분히_긴_임의의_키
LITELLM_API_KEY=위와_같은_값
```

## 3. 서버 시작

mock 지표로 RAG부터 확인:

```bash
USE_MOCK=1 docker compose --profile rag up -d --build api litellm
```

LiteLLM 로그:

```bash
docker compose logs --tail=100 litellm
```

## 4. LiteLLM 직접 테스트

`.env`를 현재 셸에 읽은 뒤 테스트합니다.

```bash
set -a
. ./.env
set +a

curl -sS http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"rag-chat",
    "messages":[{"role":"user","content":"연결 확인이라고 짧게 답해줘"}]
  }'
```

## 5. 프로젝트 인제스트

```bash
docker compose --profile rag run --rm rag-ingest
```

## 6. FastAPI RAG 테스트

```bash
curl -sS http://127.0.0.1:8000/rag/health

curl -sS -X POST http://127.0.0.1:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"역 취약도는 어떤 기준으로 계산돼?"}'

curl -sS -X POST http://127.0.0.1:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"대전역은 왜 이 등급이야?"}'
```

한 번에 smoke test:

```bash
bash scripts/rag_smoke_test.sh
```

## 7. 실제 DB 모드

기존 데이터가 준비됐다면:

```bash
USE_MOCK=0 docker compose --profile rag --profile db up -d --build api litellm db
```

자세한 구조와 프론트 연결 계약은 패치가 추가하는 `.docs/RAG_LiteLLM.md`를 참고합니다.
