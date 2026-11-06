from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class ExecutionMode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class Slots:
    """Resolved providers for one run. Mode supplies defaults; env can override."""

    llm: str
    image: str
    video: str
    tts: str

    def to_dict(self) -> dict:
        return asdict(self)


# Per-mode defaults. Env LLM_PROFILE / IMAGE_PROVIDER / VIDEO_PROVIDER / TTS_PROFILE override.
MODE_CONFIGS: dict[ExecutionMode, dict[str, str]] = {
    ExecutionMode.LOCAL: {
        "llm": "lmstudio",
        "image": "vllm_omni",
        "video": "minimax_h3",
        "tts": "qwen3_tts",
    },
    ExecutionMode.CLOUD: {
        "llm": "openrouter",
        "image": "gpt_image_2",
        "video": "seedance_2.5",
        "tts": "openai_speech",
    },
    ExecutionMode.HYBRID: {
        "llm": "lmstudio",
        "image": "vllm_omni",
        "video": "seedance_2.5",
        "tts": "qwen3_tts",
    },
}


def parse_mode(mode: str) -> ExecutionMode:
    try:
        return ExecutionMode(mode)
    except ValueError:
        return ExecutionMode.HYBRID


def resolve_mode_slots(
    mode: str,
    llm: str | None = None,
    image: str | None = None,
    video: str | None = None,
    tts: str | None = None,
) -> Slots:
    defaults = MODE_CONFIGS[parse_mode(mode)]
    return Slots(
        llm=llm or defaults["llm"],
        image=image or defaults["image"],
        video=video or defaults["video"],
        tts=tts or defaults["tts"],
    )
