"""LiteLLM Proxy OpenAI-compatible chat client."""
from __future__ import annotations

import httpx

from . import config


class LiteLLMClientError(RuntimeError):
    pass


def chat(system_prompt: str, user_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.LITELLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
    }
    try:
        with httpx.Client(timeout=config.REQUEST_TIMEOUT) as client:
            response = client.post(
                f"{config.LITELLM_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise LiteLLMClientError("LiteLLM 응답에 답변 본문이 없습니다")
        return answer.strip()
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise LiteLLMClientError(f"LiteLLM 채팅 호출 실패: {exc}") from exc
