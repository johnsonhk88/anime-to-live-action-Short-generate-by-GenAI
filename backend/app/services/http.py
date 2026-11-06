from __future__ import annotations

from typing import Any, Optional

import httpx


def join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def auth_headers(api_key: Optional[str], extra: Optional[dict[str, str]] = None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra:
        headers.update(extra)
    return headers


def request(
    method: str,
    url: str,
    *,
    api_key: Optional[str] = None,
    json: Any = None,
    headers: Optional[dict[str, str]] = None,
    timeout: float = 120.0,
    transport: httpx.BaseTransport | None = None,
) -> httpx.Response:
    merged = auth_headers(api_key, headers)
    with httpx.Client(timeout=timeout, transport=transport) as client:
        response = client.request(method, url, json=json, headers=merged)
        response.raise_for_status()
        return response
