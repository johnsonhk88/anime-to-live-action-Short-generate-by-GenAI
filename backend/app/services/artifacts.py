from __future__ import annotations

import base64
import re
from pathlib import Path

from app.core.config import get_settings


def output_path(*parts: str) -> Path:
    root = Path(get_settings().output_dir)
    if not root.is_absolute():
        root = Path.cwd() / root
    path = root.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def safe_name(text: str, limit: int = 40) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", text.strip())[:limit].strip("_").lower()
    return cleaned or "artifact"


def write_bytes(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def write_b64(path: Path, b64_data: str) -> str:
    return write_bytes(path, base64.b64decode(b64_data))
