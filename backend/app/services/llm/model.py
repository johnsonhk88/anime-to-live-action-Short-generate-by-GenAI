from __future__ import annotations

from app.core.config import get_settings, profile_api_key, profile_base_url, profile_model
from app.services.mode_factory import resolve_slots


def build_chat_model(mode: str | None = None):
    """LangChain ChatOpenAI pointed at the active OpenAI-compatible profile."""
    settings = get_settings()
    profile_id = resolve_slots(mode or settings.default_mode).llm
    base_url = profile_base_url("llm", profile_id, settings)
    model_name = profile_model("llm", profile_id, settings) or "local-model"
    api_key = profile_api_key("llm", profile_id, settings) or "not-needed"

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "langchain-openai is required to build the Deep Agents coordinator model. "
            "Install backend requirements.txt."
        ) from exc

    kwargs = {
        "model": model_name,
        "base_url": base_url,
        "api_key": api_key,
        "temperature": 0.2,
    }
    if profile_id == "openrouter":
        kwargs["default_headers"] = {
            "HTTP-Referer": "https://github.com/johnsonhk88/anime-to-live-action-Short-generate-by-GenAI",
            "X-Title": "anime-to-live-action",
        }
    return ChatOpenAI(**kwargs)
