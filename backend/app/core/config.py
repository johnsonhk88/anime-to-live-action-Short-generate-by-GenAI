from __future__ import annotations

import os
from typing import Optional

from pydantic_settings import BaseSettings

from app.core.modes import resolve_mode_slots
from app.core.profiles import (
    IMAGE_PROFILES,
    LLM_PROFILES,
    SEEDANCE_BACKENDS,
    TTS_PROFILES,
    VIDEO_PROFILES,
)

_settings_instance: Optional["Settings"] = None


class ConfigurationError(Exception):
    pass


class Settings(BaseSettings):
    default_mode: str = "hybrid"
    max_pipeline_iterations: int = 3
    mock_providers: bool = False
    output_dir: str = "./data/outputs"

    # Optional per-slot overrides (None = use MODE_CONFIGS for the active mode)
    llm_profile: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    agent_model: Optional[str] = None  # deprecated alias for llm_model

    image_provider: Optional[str] = None
    image_model: Optional[str] = None
    video_provider: Optional[str] = None
    video_model: Optional[str] = None
    tts_profile: Optional[str] = None
    tts_model: Optional[str] = None
    tts_enabled: bool = True

    seedance_backend: str = "openrouter"
    seedance_base_url: Optional[str] = None
    seedance_api_key: Optional[str] = None
    seedance_model: str = "bytedance/seedance-2.5"

    # Engine URLs
    lmstudio_base_url: str = "http://127.0.0.1:1234/v1"
    vllm_base_url: str = "http://127.0.0.1:8000/v1"
    vllm_omni_base_url: str = "http://127.0.0.1:8091/v1"
    sglang_base_url: str = "http://127.0.0.1:30000/v1"
    sglang_diffusion_base_url: str = "http://127.0.0.1:30000/v1"
    strata_base_url: str = "http://127.0.0.1:8080/v1"
    ollama_base_url: str = "http://127.0.0.1:11434/v1"
    comfyui_base_url: str = "http://127.0.0.1:8188"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    grok_base_url: str = "https://api.x.ai/v1"
    opencode_go_base_url: str = "https://opencode.ai/zen/v1"
    github_copilot_base_url: str = "https://api.githubcopilot.com"

    # Keys
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    opencode_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    github_token: Optional[str] = None
    strata_api_key: Optional[str] = None
    api_key: Optional[str] = None  # generic / Strata fallback

    langsmith_tracing: bool = False
    langsmith_api_key: Optional[str] = None

    # Backward-compat aliases used by older .env files
    lm_studio_base_url: Optional[str] = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def lmstudio_url(self) -> str:
        return self.lm_studio_base_url or self.lmstudio_base_url


def reset_settings() -> None:
    global _settings_instance
    _settings_instance = None


def _env_or_attr(settings: Settings, env_var: str) -> Optional[str]:
    attr = env_var.lower()
    return getattr(settings, attr, None) or os.environ.get(env_var) or None


def _key_for_profile(settings: Settings, env_var: str | None) -> Optional[str]:
    if not env_var:
        return None
    value = _env_or_attr(settings, env_var)
    if value:
        return value
    if env_var == "STRATA_API_KEY":
        return settings.strata_api_key or settings.api_key or os.environ.get("API_KEY")
    if env_var == "XAI_API_KEY":
        return settings.xai_api_key or os.environ.get("GROK_API_KEY")
    if env_var == "GITHUB_TOKEN":
        return settings.github_token or os.environ.get("COPILOT_API_KEY")
    if env_var == "OPENCODE_API_KEY":
        return settings.opencode_api_key or os.environ.get("OPENCODE_GO_API_KEY")
    return None


def _missing_key_error(profile_id: str, env_var: str) -> ConfigurationError:
    return ConfigurationError(
        f"\n{'=' * 70}\n"
        f"  Missing API Key for profile '{profile_id}'\n"
        f"\n"
        f"  Set the {env_var} environment variable, or set MOCK_PROVIDERS=true\n"
        f"  for local dry-runs without calling real providers.\n"
        f"\n"
        f"  Quick start:\n"
        f"    cp backend/.env.example backend/.env\n"
        f"    # Then edit backend/.env and add your API key\n"
        f"{'=' * 70}\n"
    )


def _apply_agent_model_alias(settings: Settings) -> None:
    """AGENT_MODEL=profile:model still works as a convenience alias."""
    raw = settings.agent_model
    if not raw:
        return
    if ":" in raw:
        profile, model = raw.split(":", 1)
        aliases = {"lm_studio": "lmstudio", "google_genai": "openrouter"}
        profile = aliases.get(profile, profile)
        if settings.llm_profile is None and profile in LLM_PROFILES:
            settings.llm_profile = profile
        if not settings.llm_model:
            settings.llm_model = model
    elif not settings.llm_model:
        settings.llm_model = raw


def _validate_settings(settings: Settings) -> None:
    backend = (settings.seedance_backend or "openrouter").lower()
    if backend not in SEEDANCE_BACKENDS:
        raise ConfigurationError(
            f"SEEDANCE_BACKEND must be one of {SEEDANCE_BACKENDS}, got '{settings.seedance_backend}'"
        )
    settings.seedance_backend = backend

    if settings.mock_providers:
        return

    slots = resolve_mode_slots(
        settings.default_mode,
        llm=settings.llm_profile,
        image=settings.image_provider,
        video=settings.video_provider,
        tts=settings.tts_profile if settings.tts_enabled else "none",
    )
    catalogs = (
        (slots.llm, LLM_PROFILES, "llm"),
        (slots.image, IMAGE_PROFILES, "image"),
        (slots.video, VIDEO_PROFILES, "video"),
        (slots.tts, TTS_PROFILES, "tts"),
    )
    for profile_id, catalog, kind in catalogs:
        profile = catalog.get(profile_id)
        if profile is None:
            known = ", ".join(sorted(catalog))
            raise ConfigurationError(
                f"Unknown {kind} profile '{profile_id}'. Known: {known}"
            )
        if profile.api_key_env and not _key_for_profile(settings, profile.api_key_env):
            # Seedance via OpenRouter uses OPENROUTER_API_KEY; direct uses SEEDANCE_API_KEY.
            if profile.id == "seedance_2.5" and settings.seedance_backend == "direct":
                if not (settings.seedance_api_key or os.environ.get("SEEDANCE_API_KEY")):
                    raise _missing_key_error(profile.id, "SEEDANCE_API_KEY")
                if not (settings.seedance_base_url or os.environ.get("SEEDANCE_BASE_URL")):
                    raise ConfigurationError(
                        "SEEDANCE_BASE_URL is required when SEEDANCE_BACKEND=direct"
                    )
                continue
            raise _missing_key_error(profile.id, profile.api_key_env)


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is not None:
        return _settings_instance

    settings = Settings()
    _apply_agent_model_alias(settings)
    _validate_settings(settings)
    _settings_instance = settings
    return _settings_instance


def profile_base_url(kind: str, profile_id: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    explicit = {
        "lmstudio": settings.lmstudio_url(),
        "vllm": settings.vllm_base_url,
        "vllm_omni": settings.vllm_omni_base_url,
        "sglang": settings.sglang_base_url,
        "sglang_diffusion": settings.sglang_diffusion_base_url,
        "strata": settings.strata_base_url,
        "ollama": settings.ollama_base_url,
        "comfyui": settings.comfyui_base_url,
        "comfy_tts": settings.comfyui_base_url,
        "minimax_h3": settings.comfyui_base_url,
        "ltx_2.5": settings.comfyui_base_url,
        "openrouter": settings.openrouter_base_url,
        "grok": settings.grok_base_url,
        "opencode_go": settings.opencode_go_base_url,
        "github_copilot": settings.github_copilot_base_url,
        "gpt_image_2": "https://api.openai.com/v1",
        "openai_speech": "https://api.openai.com/v1",
        "nano_banana_2": "https://generativelanguage.googleapis.com/v1beta",
        "seedance_2.5": (
            settings.seedance_base_url
            or (
                settings.openrouter_base_url
                if settings.seedance_backend == "openrouter"
                else ""
            )
        ),
        "veo": "https://generativelanguage.googleapis.com/v1beta",
        "none": "",
    }
    if kind == "llm" and settings.llm_base_url:
        return settings.llm_base_url.rstrip("/")
    url = explicit.get(profile_id)
    if url:
        return url.rstrip("/")
    catalogs = {"llm": LLM_PROFILES, "image": IMAGE_PROFILES, "video": VIDEO_PROFILES, "tts": TTS_PROFILES}
    profile = catalogs[kind].get(profile_id)
    return (profile.default_base_url if profile else "").rstrip("/")


def profile_api_key(kind: str, profile_id: str, settings: Settings | None = None) -> Optional[str]:
    settings = settings or get_settings()
    if kind == "llm" and settings.llm_api_key:
        return settings.llm_api_key
    if profile_id == "seedance_2.5":
        if settings.seedance_backend == "direct":
            return settings.seedance_api_key or os.environ.get("SEEDANCE_API_KEY")
        return _key_for_profile(settings, "OPENROUTER_API_KEY")
    catalogs = {"llm": LLM_PROFILES, "image": IMAGE_PROFILES, "video": VIDEO_PROFILES, "tts": TTS_PROFILES}
    profile = catalogs[kind].get(profile_id)
    if not profile:
        return None
    return _key_for_profile(settings, profile.api_key_env)


def profile_model(kind: str, profile_id: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    override = {
        "llm": settings.llm_model,
        "image": settings.image_model,
        "video": settings.video_model if profile_id != "seedance_2.5" else settings.video_model or settings.seedance_model,
        "tts": settings.tts_model,
    }.get(kind)
    if override:
        return override
    catalogs = {"llm": LLM_PROFILES, "image": IMAGE_PROFILES, "video": VIDEO_PROFILES, "tts": TTS_PROFILES}
    profile = catalogs[kind].get(profile_id)
    return profile.default_model if profile else ""
