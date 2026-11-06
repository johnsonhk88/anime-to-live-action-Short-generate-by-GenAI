"""Named engine profiles. Each profile is a base_url + optional API key env.

LLM engines all speak OpenAI-compatible /chat/completions.
Image/TTS engines use /images/generations and /audio/speech where noted.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineProfile:
    id: str
    kind: str  # llm | image | video | tts
    default_base_url: str
    default_model: str
    api_key_env: str | None
    local: bool
    notes: str = ""


LLM_PROFILES: dict[str, EngineProfile] = {
    "lmstudio": EngineProfile(
        id="lmstudio",
        kind="llm",
        default_base_url="http://127.0.0.1:1234/v1",
        default_model="",
        api_key_env=None,
        local=True,
        notes="Desktop OpenAI-compatible server (default local LLM).",
    ),
    "vllm": EngineProfile(
        id="vllm",
        kind="llm",
        default_base_url="http://127.0.0.1:8000/v1",
        default_model="",
        api_key_env=None,
        local=True,
        notes="docker-vllm-serving-engine text LLM.",
    ),
    "vllm_omni": EngineProfile(
        id="vllm_omni",
        kind="llm",
        default_base_url="http://127.0.0.1:8091/v1",
        default_model="",
        api_key_env=None,
        local=True,
        notes="vLLM-Omni: vision chat, Qwen-Image, Qwen3-TTS on one server.",
    ),
    "sglang": EngineProfile(
        id="sglang",
        kind="llm",
        default_base_url="http://127.0.0.1:30000/v1",
        default_model="",
        api_key_env=None,
        local=True,
        notes="sglang-llm-inference-engine text LLM.",
    ),
    "strata": EngineProfile(
        id="strata",
        kind="llm",
        default_base_url="http://127.0.0.1:8080/v1",
        default_model="",
        api_key_env="STRATA_API_KEY",
        local=True,
        notes="strata-llm-inference-engine. Bearer key required.",
    ),
    "ollama": EngineProfile(
        id="ollama",
        kind="llm",
        default_base_url="http://127.0.0.1:11434/v1",
        default_model="llama3",
        api_key_env=None,
        local=True,
    ),
    "openrouter": EngineProfile(
        id="openrouter",
        kind="llm",
        default_base_url="https://openrouter.ai/api/v1",
        default_model="anthropic/claude-sonnet-4.6",
        api_key_env="OPENROUTER_API_KEY",
        local=False,
        notes="Default cloud LLM. Also used as Seedance OpenRouter backend.",
    ),
    "grok": EngineProfile(
        id="grok",
        kind="llm",
        default_base_url="https://api.x.ai/v1",
        default_model="grok-4",
        api_key_env="XAI_API_KEY",
        local=False,
    ),
    "opencode_go": EngineProfile(
        id="opencode_go",
        kind="llm",
        default_base_url="https://opencode.ai/zen/v1",
        default_model="",
        api_key_env="OPENCODE_API_KEY",
        local=False,
        notes="OpenCode Go subscription. Override OPENCODE_GO_BASE_URL if needed.",
    ),
    "github_copilot": EngineProfile(
        id="github_copilot",
        kind="llm",
        default_base_url="https://api.githubcopilot.com",
        default_model="",
        api_key_env="GITHUB_TOKEN",
        local=False,
        notes="Copilot models API. Prefer a Copilot token; OAuth is a later wave.",
    ),
}

IMAGE_PROFILES: dict[str, EngineProfile] = {
    "vllm_omni": EngineProfile(
        id="vllm_omni",
        kind="image",
        default_base_url="http://127.0.0.1:8091/v1",
        default_model="qwen-image",
        api_key_env=None,
        local=True,
        notes="POST /images/generations (Qwen-Image, Qwen-Image-Edit).",
    ),
    "sglang_diffusion": EngineProfile(
        id="sglang_diffusion",
        kind="image",
        default_base_url="http://127.0.0.1:30000/v1",
        default_model="Qwen/Qwen-Image",
        api_key_env=None,
        local=True,
        notes="SGLang Diffusion OpenAI-compatible image API.",
    ),
    "comfyui": EngineProfile(
        id="comfyui",
        kind="image",
        default_base_url="http://127.0.0.1:8188",
        default_model="",
        api_key_env=None,
        local=True,
        notes="ComfyUI HTTP /prompt queue.",
    ),
    "gpt_image_2": EngineProfile(
        id="gpt_image_2",
        kind="image",
        default_base_url="https://api.openai.com/v1",
        default_model="gpt-image-2",
        api_key_env="OPENAI_API_KEY",
        local=False,
        notes="Default cloud image. Character sheets / identity from reference.",
    ),
    "nano_banana_2": EngineProfile(
        id="nano_banana_2",
        kind="image",
        default_base_url="https://generativelanguage.googleapis.com/v1beta",
        default_model="gemini-3.1-flash-image",
        api_key_env="GOOGLE_API_KEY",
        local=False,
        notes="Google Nano Banana 2 (Gemini image). Optional, not required.",
    ),
}

VIDEO_PROFILES: dict[str, EngineProfile] = {
    "seedance_2.5": EngineProfile(
        id="seedance_2.5",
        kind="video",
        default_base_url="https://openrouter.ai/api/v1",
        default_model="bytedance/seedance-2.5",
        api_key_env="OPENROUTER_API_KEY",
        local=False,
        notes="Default cloud video. Backend openrouter|direct (SEEDANCE_BACKEND).",
    ),
    "minimax_h3": EngineProfile(
        id="minimax_h3",
        kind="video",
        default_base_url="http://127.0.0.1:8188",
        default_model="minimax-h3",
        api_key_env=None,
        local=True,
        notes="Local live-action via ComfyUI MiniMax H3 workflows.",
    ),
    "ltx_2.5": EngineProfile(
        id="ltx_2.5",
        kind="video",
        default_base_url="http://127.0.0.1:8188",
        default_model="ltx-2.5",
        api_key_env=None,
        local=True,
        notes="Local draft/iteration via ComfyUI LTX-2.5 workflows.",
    ),
    "veo": EngineProfile(
        id="veo",
        kind="video",
        default_base_url="https://generativelanguage.googleapis.com/v1beta",
        default_model="veo-3.1",
        api_key_env="GOOGLE_API_KEY",
        local=False,
        notes="Optional fallback. Not the default cloud video path.",
    ),
}

TTS_PROFILES: dict[str, EngineProfile] = {
    "qwen3_tts": EngineProfile(
        id="qwen3_tts",
        kind="tts",
        default_base_url="http://127.0.0.1:8091/v1",
        default_model="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        api_key_env=None,
        local=True,
        notes="vLLM-Omni POST /audio/speech. CustomVoice / VoiceDesign / Base clone.",
    ),
    "cosyvoice3": EngineProfile(
        id="cosyvoice3",
        kind="tts",
        default_base_url="http://127.0.0.1:8091/v1",
        default_model="FunAudioLLM/Fun-CosyVoice3-0.5B-2512",
        api_key_env=None,
        local=True,
        notes="vLLM-Omni voice clone via ref_audio + ref_text.",
    ),
    "comfy_tts": EngineProfile(
        id="comfy_tts",
        kind="tts",
        default_base_url="http://127.0.0.1:8188",
        default_model="",
        api_key_env=None,
        local=True,
        notes="ComfyUI Qwen-TTS (or similar) nodes.",
    ),
    "openai_speech": EngineProfile(
        id="openai_speech",
        kind="tts",
        default_base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini-tts",
        api_key_env="OPENAI_API_KEY",
        local=False,
    ),
    "none": EngineProfile(
        id="none",
        kind="tts",
        default_base_url="",
        default_model="",
        api_key_env=None,
        local=True,
        notes="TTS disabled. Use native Seedance/H3 audio only.",
    ),
}

SEEDANCE_BACKENDS = ("openrouter", "direct")


def require_profile(catalog: dict[str, EngineProfile], profile_id: str, kind: str) -> EngineProfile:
    profile = catalog.get(profile_id)
    if profile is None:
        known = ", ".join(sorted(catalog))
        raise KeyError(f"Unknown {kind} profile '{profile_id}'. Known: {known}")
    return profile
