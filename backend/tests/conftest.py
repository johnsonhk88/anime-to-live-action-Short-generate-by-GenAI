import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

os.environ["MOCK_PROVIDERS"] = "true"
os.environ.setdefault("DEFAULT_MODE", "hybrid")
os.environ.setdefault("MAX_PIPELINE_ITERATIONS", "3")
os.environ.setdefault("SEEDANCE_BACKEND", "openrouter")

from app.core.config import reset_settings

reset_settings()


@pytest.fixture(autouse=True)
def isolate_settings(monkeypatch, tmp_path):
    """Keep tests off backend/.env so slot defaults are deterministic."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MOCK_PROVIDERS", "true")
    monkeypatch.setenv("DEFAULT_MODE", "hybrid")
    monkeypatch.setenv("SEEDANCE_BACKEND", "openrouter")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/workflow.db")
    for key in (
        "LLM_PROFILE",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "LLM_API_KEY",
        "AGENT_MODEL",
        "IMAGE_PROVIDER",
        "IMAGE_MODEL",
        "VIDEO_PROVIDER",
        "VIDEO_MODEL",
        "TTS_PROFILE",
        "TTS_MODEL",
        "TTS_ENABLED",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    reset_settings()
    yield
    reset_settings()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient fixture that mocks the pipeline agent before app startup."""
    from unittest.mock import MagicMock, patch

    from app.main import app

    reset_settings()

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [MagicMock(content="Pipeline completed successfully. Final video: /output/final.mp4")]
    }

    with patch("app.main.create_pipeline_agent", return_value=mock_agent):
        with TestClient(app) as client:
            yield client


@pytest.fixture
def sample_clip_path() -> str:
    return "/test/sample_anime.mp4"


@pytest.fixture
def sample_analysis_result() -> dict:
    return {
        "scenes": [
            {"id": 1, "start": 0.0, "end": 5.5, "description": "Hero arrives"}
        ],
        "characters": [
            {
                "name": "Hero",
                "role": "protagonist",
                "appearance": "Spiky dark hair",
                "key_features": ["scar"],
                "color_palette": ["#1a1a2e"],
            }
        ],
        "motion_data": {"camera_movements": ["pan_left"], "pace": "dynamic"},
        "style_notes": "Dark fantasy aesthetic",
        "provider": "lmstudio",
    }


@pytest.fixture
def sample_character_design() -> dict:
    return {
        "name": "Hero",
        "live_action_appearance": {
            "face": "Strong jawline",
            "hair": "Spiky dark hair",
            "eyes": "Intense",
            "build": "Athletic",
        },
        "wardrobe": {"primary_outfit": "Modern reinterpretation", "colors": ["#1a1a2e"]},
        "casting_notes": "Needs strong actor",
        "reference_prompts": ["cinematic portrait of Hero"],
    }
