import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient

# Set env vars BEFORE any app imports
os.environ.setdefault("AGENT_MODEL", "ollama:llama3")
os.environ.setdefault("DEFAULT_MODE", "hybrid")
os.environ.setdefault("MAX_PIPELINE_ITERATIONS", "3")

# Reset settings cache at module import time
import app.core.config as _config
_config._settings_instance = None


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient fixture that mocks the pipeline agent before app startup."""
    from unittest.mock import patch, MagicMock
    from app.main import app
    from app.core.config import _settings_instance

    # Reset settings cache so app startup creates fresh config
    _settings_instance = None

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [MagicMock(content="Pipeline completed successfully. Final video: /output/final.mp4")]
    }

    # Patch create_pipeline_agent BEFORE the app starts (lifespan calls it via app.agents.graph)
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
        "provider": "lm_studio",
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
