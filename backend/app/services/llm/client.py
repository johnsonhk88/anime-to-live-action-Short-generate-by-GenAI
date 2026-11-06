from __future__ import annotations

from typing import Any, Optional

import httpx

from app.core.config import get_settings, profile_api_key, profile_base_url, profile_model
from app.core.profiles import LLM_PROFILES, require_profile
from app.services.http import join_url, request
from app.services.mode_factory import resolve_slots


def extract_content(choice: Any) -> str:
    """Pull visible text from a chat completion choice.

    Reasoning models (Qwen, DeepSeek-R1, etc.) often put the answer in
    `reasoning_content` when `content` is empty.
    """
    if choice is None:
        return ""
    if not isinstance(choice, dict):
        message = getattr(choice, "message", None)
        if message is None:
            return str(choice)
        content = getattr(message, "content", None) or ""
        if isinstance(content, str) and content.strip():
            return content
        return getattr(message, "reasoning_content", None) or content or ""

    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    if str(content).strip():
        return str(content)
    return msg.get("reasoning_content") or ""


class OpenAICompatClient:
    """Thin OpenAI-compatible chat client. No LiteLLM."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        model: str = "",
        timeout: float = 120.0,
        transport: httpx.BaseTransport | None = None,
        extra_headers: Optional[dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "not-needed"
        self.model = model
        self.timeout = timeout
        self.transport = transport
        self.extra_headers = extra_headers or {}

    def chat(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        temperature: float = 0.2,
        extra_body: Optional[dict] = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if extra_body:
            payload.update(extra_body)
        response = request(
            "POST",
            join_url(self.base_url, "chat/completions"),
            api_key=self.api_key,
            json=payload,
            headers=self.extra_headers or None,
            timeout=self.timeout,
            transport=self.transport,
        )
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"Empty chat response from {self.base_url}: {data}")
        return extract_content(choices[0])

    def list_models(self) -> list[str]:
        response = request(
            "GET",
            join_url(self.base_url, "models"),
            api_key=self.api_key,
            headers=self.extra_headers or None,
            timeout=min(self.timeout, 10.0),
            transport=self.transport,
        )
        data = response.json()
        return [item.get("id", "") for item in data.get("data", []) if item.get("id")]

    def health(self) -> bool:
        try:
            self.list_models()
            return True
        except Exception:
            return False


def get_llm_client(mode: str = "hybrid", transport: httpx.BaseTransport | None = None) -> OpenAICompatClient:
    settings = get_settings()
    profile_id = resolve_slots(mode).llm
    require_profile(LLM_PROFILES, profile_id, "llm")
    extra = {}
    if profile_id == "openrouter":
        extra = {
            "HTTP-Referer": "https://github.com/johnsonhk88/anime-to-live-action-Short-generate-by-GenAI",
            "X-Title": "anime-to-live-action",
        }
    return OpenAICompatClient(
        base_url=profile_base_url("llm", profile_id, settings),
        api_key=profile_api_key("llm", profile_id, settings),
        model=profile_model("llm", profile_id, settings),
        transport=transport,
        extra_headers=extra,
    )
