from __future__ import annotations

from app.core.config import get_settings
from app.core.modes import ExecutionMode, Slots, resolve_mode_slots
from app.core.profiles import IMAGE_PROFILES, LLM_PROFILES, TTS_PROFILES, VIDEO_PROFILES


def resolve_slots(mode: str) -> Slots:
    settings = get_settings()
    tts_profile = settings.tts_profile
    if not settings.tts_enabled:
        tts_profile = "none"
    return resolve_mode_slots(
        mode,
        llm=settings.llm_profile,
        image=settings.image_provider,
        video=settings.video_provider,
        tts=tts_profile,
    )


def resolve_providers(mode: str) -> dict:
    """Capability map for a mode. Unknown mode falls back to hybrid."""
    slots = resolve_slots(mode)
    return {
        "llm": slots.llm,
        "analysis": slots.llm,
        "image": slots.image,
        "image_gen": slots.image,
        "video": slots.video,
        "video_gen": slots.video,
        "tts": slots.tts,
    }


def get_analysis_provider(mode: str) -> str:
    return resolve_slots(mode).llm


def get_image_gen_provider(mode: str) -> str:
    return resolve_slots(mode).image


def get_video_gen_provider(mode: str) -> str:
    return resolve_slots(mode).video


def get_tts_provider(mode: str) -> str:
    return resolve_slots(mode).tts


def is_mock() -> bool:
    return get_settings().mock_providers


def known_profiles() -> dict[str, list[str]]:
    return {
        "llm": sorted(LLM_PROFILES),
        "image": sorted(IMAGE_PROFILES),
        "video": sorted(VIDEO_PROFILES),
        "tts": sorted(TTS_PROFILES),
        "modes": [m.value for m in ExecutionMode],
    }
