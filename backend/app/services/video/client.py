from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.core.config import get_settings, profile_api_key, profile_base_url, profile_model
from app.core.profiles import VIDEO_PROFILES, require_profile
from app.services.artifacts import output_path, safe_name, write_bytes
from app.services.http import join_url, request
from app.services.mode_factory import resolve_slots


@dataclass
class VideoResult:
    clip_path: str
    provider: str
    model: str
    duration: float
    resolution: str = "1280x720"
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "clip_path": self.clip_path,
            "duration": self.duration,
            "resolution": self.resolution,
            "provider": self.provider,
            "model": self.model,
            **self.extra,
        }


def _download(url: str, dest: Path) -> str:
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https"):
        response = httpx.get(url, timeout=300.0, follow_redirects=True)
        response.raise_for_status()
        return write_bytes(dest, response.content)
    return url


def _poll_until(url: str, api_key: Optional[str], timeout: float = 600.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = request("GET", url, api_key=api_key, timeout=30.0)
        data = response.json()
        status = (data.get("status") or data.get("state") or "").lower()
        if status in ("completed", "succeeded", "success"):
            return data
        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Video job failed: {data}")
        time.sleep(3)
    raise TimeoutError(f"Timed out polling {url}")


def _seedance_openrouter(
    *,
    base_url: str,
    api_key: Optional[str],
    model: str,
    prompt: str,
    duration: float,
    resolution: str,
    aspect_ratio: str,
    generate_audio: bool,
    image_urls: list[str],
) -> VideoResult:
    content: list[dict] = [{"type": "text", "text": prompt}]
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})
    response = request(
        "POST",
        join_url(base_url, "chat/completions"),
        api_key=api_key,
        json={
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "modalities": ["video", "audio"] if generate_audio else ["video"],
        },
        headers={
            "HTTP-Referer": "https://github.com/johnsonhk88/anime-to-live-action-Short-generate-by-GenAI",
            "X-Title": "anime-to-live-action",
        },
        timeout=600.0,
    )
    payload = response.json()
    dest = output_path("clips", f"{safe_name(prompt)}_seedance.mp4")
    video_url = None
    choices = payload.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        videos = message.get("videos") or payload.get("videos") or []
        if videos:
            video_url = videos[0].get("url") or videos[0].get("video_url")
        content = message.get("content")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") in ("video_url", "video"):
                    video_url = (part.get("video_url") or {}).get("url") or part.get("url")
    if not video_url:
        video_url = payload.get("url") or (payload.get("output") or {}).get("url")
    if video_url:
        _download(video_url, dest)
    return VideoResult(
        clip_path=str(dest) if dest.exists() else (video_url or str(dest)),
        provider="seedance_2.5",
        model=model,
        duration=duration,
        resolution=resolution,
        extra={"backend": "openrouter", "aspect_ratio": aspect_ratio, "raw_keys": list(payload.keys())},
    )


def _seedance_direct(
    *,
    base_url: str,
    api_key: Optional[str],
    model: str,
    prompt: str,
    duration: float,
    resolution: str,
    aspect_ratio: str,
    generate_audio: bool,
    image_urls: list[str],
) -> VideoResult:
    if not base_url:
        raise RuntimeError("SEEDANCE_BASE_URL is required when SEEDANCE_BACKEND=direct")
    body = {
        "model": model,
        "prompt": prompt,
        "duration": int(duration),
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
    }
    if image_urls:
        body["image"] = image_urls[0]
        body["reference_images"] = image_urls
    response = request(
        "POST",
        join_url(base_url, "v1/videos"),
        api_key=api_key,
        json=body,
        timeout=60.0,
    )
    payload = response.json()
    job_id = payload.get("id") or payload.get("request_id") or (payload.get("data") or {}).get("id")
    poll_url = payload.get("polling_url") or (join_url(base_url, f"v1/videos/{job_id}") if job_id else None)
    if poll_url:
        payload = _poll_until(poll_url, api_key)
    dest = output_path("clips", f"{safe_name(prompt)}_seedance.mp4")
    video_url = (
        payload.get("url")
        or payload.get("output_url")
        or (payload.get("output") or {}).get("url")
        or (payload.get("data") or {}).get("output_url")
    )
    if video_url:
        _download(video_url, dest)
    return VideoResult(
        clip_path=str(dest) if dest.exists() else (video_url or str(dest)),
        provider="seedance_2.5",
        model=model,
        duration=duration,
        resolution=resolution,
        extra={"backend": "direct", "job_id": job_id},
    )


def _comfy_video(provider: str, base_url: str, prompt: str, duration: float) -> VideoResult:
    workflow_name = "minimax_h3.json" if provider == "minimax_h3" else "ltx_2.5.json"
    workflow_path = Path("workflows") / workflow_name
    if not workflow_path.exists():
        raise RuntimeError(
            f"Local video provider '{provider}' needs backend/workflows/{workflow_name}."
        )
    import json

    workflow = json.loads(workflow_path.read_text())
    response = request("POST", join_url(base_url, "prompt"), json={"prompt": workflow}, timeout=30.0)
    dest = output_path("clips", f"{safe_name(prompt)}_{provider}.mp4")
    return VideoResult(
        clip_path=str(dest),
        provider=provider,
        model=provider,
        duration=duration,
        extra={"prompt_id": response.json().get("prompt_id"), "pending": True},
    )


class VideoClient:
    def __init__(self, provider: str, mode: str = "hybrid"):
        self.provider = provider
        self.mode = mode
        self.settings = get_settings()

    def generate(
        self,
        prompt: str,
        *,
        duration: float = 8.0,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        generate_audio: bool = True,
        image_urls: Optional[list[str]] = None,
    ) -> VideoResult:
        require_profile(VIDEO_PROFILES, self.provider, "video")
        image_urls = image_urls or []
        if self.provider == "seedance_2.5":
            model = profile_model("video", self.provider, self.settings)
            api_key = profile_api_key("video", self.provider, self.settings)
            if self.settings.seedance_backend == "direct":
                return _seedance_direct(
                    base_url=self.settings.seedance_base_url or "",
                    api_key=api_key,
                    model=model,
                    prompt=prompt,
                    duration=duration,
                    resolution=resolution,
                    aspect_ratio=aspect_ratio,
                    generate_audio=generate_audio,
                    image_urls=image_urls,
                )
            return _seedance_openrouter(
                base_url=profile_base_url("video", self.provider, self.settings),
                api_key=api_key,
                model=model,
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                generate_audio=generate_audio,
                image_urls=image_urls,
            )
        if self.provider in ("minimax_h3", "ltx_2.5"):
            return _comfy_video(
                self.provider,
                profile_base_url("video", self.provider, self.settings),
                prompt,
                duration,
            )
        raise RuntimeError(
            f"Video provider '{self.provider}' is not implemented yet "
            f"(veo is an optional fallback, not the default path)."
        )


def get_video_client(mode: str = "hybrid") -> VideoClient:
    return VideoClient(resolve_slots(mode).video, mode=mode)


def generate_video(prompt: str, mode: str = "hybrid", **kwargs) -> VideoResult:
    return get_video_client(mode).generate(prompt, **kwargs)
