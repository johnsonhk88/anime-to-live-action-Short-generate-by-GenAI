from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.core.config import get_settings, profile_api_key, profile_base_url, profile_model
from app.core.profiles import IMAGE_PROFILES, require_profile
from app.services.artifacts import output_path, safe_name, write_b64, write_bytes
from app.services.http import join_url, request
from app.services.mode_factory import resolve_slots


@dataclass
class ImageResult:
    image_path: str
    provider: str
    model: str
    prompt: str
    resolution: str = "1024x1024"
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "image_path": self.image_path,
            "resolution": self.resolution,
            "provider": self.provider,
            "model": self.model,
            **self.extra,
        }


def _save_from_response(provider: str, prompt: str, payload: dict) -> Path:
    dest = output_path("references", f"{safe_name(prompt)}_{provider}.png")
    data = payload.get("data") or []
    if not data:
        raise RuntimeError(f"{provider} image response missing data: {payload}")
    item = data[0]
    if item.get("b64_json"):
        write_b64(dest, item["b64_json"])
        return dest
    url = item.get("url")
    if url:
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https"):
            response = httpx.get(url, timeout=60.0)
            response.raise_for_status()
            write_bytes(dest, response.content)
            return dest
        write_bytes(dest, Path(url).read_bytes())
        return dest
    raise RuntimeError(f"{provider} image response had no b64_json or url")


def _openai_images(
    *,
    base_url: str,
    api_key: Optional[str],
    model: str,
    prompt: str,
    size: str,
    provider: str,
    extra_headers: Optional[dict] = None,
    timeout: float = 180.0,
    image_url: Optional[str] = None,
) -> ImageResult:
    body: dict = {"model": model, "prompt": prompt, "n": 1, "size": size}
    path = "images/edits" if image_url else "images/generations"
    if image_url:
        body["image"] = image_url
    response = request(
        "POST",
        join_url(base_url, path),
        api_key=api_key,
        json=body,
        headers=extra_headers,
        timeout=timeout,
    )
    dest = _save_from_response(provider, prompt, response.json())
    return ImageResult(
        image_path=str(dest),
        provider=provider,
        model=model,
        prompt=prompt,
        resolution=size,
    )


def _nano_banana(prompt: str, model: str, api_key: Optional[str], size: str) -> ImageResult:
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is required for nano_banana_2")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response = request(
        "POST",
        url,
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
        },
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        timeout=180.0,
    )
    dest = output_path("references", f"{safe_name(prompt)}_nano_banana.png")
    payload = response.json()
    for candidate in payload.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data") or {}
            data = inline.get("data")
            if data:
                write_b64(dest, data)
                return ImageResult(str(dest), "nano_banana_2", model, prompt, size)
    raise RuntimeError(f"nano_banana_2 returned no image: {payload}")


def _comfy_image(base_url: str, prompt: str, size: str) -> ImageResult:
    """Queue a txt2img job. Requires a workflow at workflows/txt2img.json when not mocked."""
    dest = output_path("references", f"{safe_name(prompt)}_comfy.png")
    workflow_path = Path("workflows/txt2img.json")
    if not workflow_path.exists():
        raise RuntimeError(
            "ComfyUI image generation needs backend/workflows/txt2img.json. "
            "Set IMAGE_PROVIDER=vllm_omni or gpt_image_2, or add a Comfy workflow."
        )
    import json

    workflow = json.loads(workflow_path.read_text())
    response = request(
        "POST",
        join_url(base_url, "prompt"),
        json={"prompt": workflow},
        timeout=30.0,
    )
    prompt_id = response.json().get("prompt_id")
    return ImageResult(
        image_path=str(dest),
        provider="comfyui",
        model="comfyui",
        prompt=prompt,
        resolution=size,
        extra={"prompt_id": prompt_id, "pending": True},
    )


class ImageClient:
    def __init__(self, provider: str, mode: str = "hybrid"):
        self.provider = provider
        self.mode = mode
        self.settings = get_settings()

    def generate(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        image_url: Optional[str] = None,
    ) -> ImageResult:
        require_profile(IMAGE_PROFILES, self.provider, "image")
        model = profile_model("image", self.provider, self.settings)
        base_url = profile_base_url("image", self.provider, self.settings)
        api_key = profile_api_key("image", self.provider, self.settings)

        if self.provider in ("vllm_omni", "sglang_diffusion"):
            return _openai_images(
                base_url=base_url,
                api_key=api_key,
                model=model,
                prompt=prompt,
                size=size,
                provider=self.provider,
            )
        if self.provider == "gpt_image_2":
            return _openai_images(
                base_url=base_url,
                api_key=api_key,
                model=model,
                prompt=prompt,
                size=size,
                provider=self.provider,
                image_url=image_url,
            )
        if self.provider == "nano_banana_2":
            return _nano_banana(prompt, model, api_key, size)
        if self.provider == "comfyui":
            return _comfy_image(base_url, prompt, size)
        raise RuntimeError(f"Unsupported image provider: {self.provider}")


def get_image_client(mode: str = "hybrid") -> ImageClient:
    return ImageClient(resolve_slots(mode).image, mode=mode)


def generate_image(prompt: str, mode: str = "hybrid", **kwargs) -> ImageResult:
    return get_image_client(mode).generate(prompt, **kwargs)
