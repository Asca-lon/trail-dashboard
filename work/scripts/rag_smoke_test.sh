#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"

echo "[1/3] RAG health"
curl -fsS "${API_BASE_URL}/rag/health"
echo

echo "[2/3] project document question"
curl -fsS -X POST "${API_BASE_URL}/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"역 취약도는 어떤 기준으로 계산돼?"}'
echo

echo "[3/3] station metric + RAG question"
curl -fsS -X POST "${API_BASE_URL}/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"대전역은 왜 이 등급이야?"}'
echo
