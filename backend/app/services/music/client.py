from __future__ import annotations

import wave
from dataclasses import dataclass

from app.services.artifacts import output_path, safe_name
from app.services.mode_factory import is_mock


@dataclass
class MusicResult:
    audio_path: str
    provider: str
    prompt: str
    duration: float

    def to_dict(self) -> dict:
        return {
            "audio_path": self.audio_path,
            "provider": self.provider,
            "prompt": self.prompt,
            "duration": self.duration,
        }


def _write_silence(path, seconds: float, rate: int = 22050) -> None:
    frames = int(max(seconds, 0.5) * rate)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\x00\x00" * frames)


def generate_bgm(prompt: str, duration: float = 30.0) -> MusicResult:
    """Generate a score bed. First slice: silent WAV placeholder (mock or no music engine)."""
    dest = output_path("music", f"{safe_name(prompt or 'score')}.wav")
    _write_silence(dest, duration)
    provider = "mock_silence" if is_mock() else "placeholder_silence"
    return MusicResult(str(dest), provider, prompt, duration)
