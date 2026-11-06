from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.core.config import get_settings, profile_api_key, profile_base_url, profile_model
from app.core.profiles import TTS_PROFILES, require_profile
from app.services.artifacts import output_path, safe_name, write_bytes
from app.services.http import join_url, request
from app.services.mode_factory import resolve_slots


@dataclass
class AudioResult:
    audio_path: str
    provider: str
    model: str
    text: str
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "audio_path": self.audio_path,
            "provider": self.provider,
            "model": self.model,
            "text": self.text,
            **self.extra,
        }


class TtsClient:
    def __init__(self, provider: str, mode: str = "hybrid"):
        self.provider = provider
        self.mode = mode
        self.settings = get_settings()

    def synthesize(
        self,
        text: str,
        *,
        voice: str = "narrator",
        response_format: str = "wav",
        ref_audio: Optional[str] = None,
        ref_text: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> AudioResult:
        if self.provider in ("none", "", None):
            raise RuntimeError("TTS is disabled (tts profile 'none').")
        require_profile(TTS_PROFILES, self.provider, "tts")
        model = profile_model("tts", self.provider, self.settings)
        base_url = profile_base_url("tts", self.provider, self.settings)
        api_key = profile_api_key("tts", self.provider, self.settings)
        if self.provider == "comfy_tts":
            raise RuntimeError("comfy_tts requires a Comfy workflow; use qwen3_tts on vLLM-Omni.")

        body = {
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": response_format,
        }
        if instructions:
            body["instructions"] = instructions
        if ref_audio:
            body["ref_audio"] = ref_audio
        if ref_text:
            body["ref_text"] = ref_text

        response = request(
            "POST",
            join_url(base_url, "audio/speech"),
            api_key=api_key,
            json=body,
            timeout=180.0,
        )
        dest = output_path("audio", f"{safe_name(voice)}_{safe_name(text, 24)}.{response_format}")
        write_bytes(dest, response.content)
        return AudioResult(str(dest), self.provider, model, text, extra={"voice": voice})


def get_tts_client(mode: str = "hybrid") -> TtsClient:
    return TtsClient(resolve_slots(mode).tts, mode=mode)


def synthesize_speech(text: str, mode: str = "hybrid", **kwargs) -> AudioResult:
    return get_tts_client(mode).synthesize(text, **kwargs)
