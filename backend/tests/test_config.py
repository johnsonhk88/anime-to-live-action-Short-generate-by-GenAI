"""Tests for configuration and settings."""

import os
import pytest
from app.core.config import Settings, get_settings, ConfigurationError, MODEL_API_KEY_MAP


class TestSettings:
    def test_default_values(self, monkeypatch):
        # Remove env vars that would override defaults so we test class defaults
        monkeypatch.delenv("AGENT_MODEL", raising=False)
        monkeypatch.delenv("DEFAULT_MODE", raising=False)
        settings = Settings(_env_file=None)
        assert settings.agent_model == "google_genai:gemini-3.5-flash"
        assert settings.default_mode == "hybrid"
        assert settings.max_pipeline_iterations == 3
        assert settings.langsmith_tracing is False

    def test_env_override(self, monkeypatch):
        monkeypatch.delenv("AGENT_MODEL", raising=False)
        monkeypatch.delenv("DEFAULT_MODE", raising=False)
        monkeypatch.setenv("AGENT_MODEL", "anthropic:claude-sonnet-4-6")
        monkeypatch.setenv("DEFAULT_MODE", "local")
        monkeypatch.setenv("MAX_PIPELINE_ITERATIONS", "5")
        settings = Settings(_env_file=None)
        assert settings.agent_model == "anthropic:claude-sonnet-4-6"
        assert settings.default_mode == "local"
        assert settings.max_pipeline_iterations == 5

    def test_api_key_fields_are_optional(self, monkeypatch):
        monkeypatch.delenv("AGENT_MODEL", raising=False)
        settings = Settings(_env_file=None)
        assert settings.google_api_key is None
        assert settings.openai_api_key is None
        assert settings.anthropic_api_key is None


class TestModelApiKeyMap:
    def test_google_genai_needs_key(self):
        assert MODEL_API_KEY_MAP["google_genai"] == "GOOGLE_API_KEY"

    def test_ollama_no_key_needed(self):
        assert MODEL_API_KEY_MAP["ollama"] is None

    def test_openai_needs_key(self):
        assert MODEL_API_KEY_MAP["openai"] == "OPENAI_API_KEY"

    def test_all_known_providers_mapped(self):
        expected = {"google_genai", "openai", "anthropic", "ollama",
                    "azure_openai", "bedrock", "huggingface",
                    "openrouter", "fireworks", "baseten"}
        assert set(MODEL_API_KEY_MAP.keys()) == expected


class TestGetSettings:
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        import app.core.config as _config
        _config._settings_instance = None
        yield

    def test_valid_model_no_key_needed(self, monkeypatch):
        monkeypatch.setenv("AGENT_MODEL", "ollama:llama3")
        monkeypatch.setenv("DEFAULT_MODE", "hybrid")
        settings = get_settings()
        assert settings.agent_model == "ollama:llama3"

    def test_raises_on_missing_api_key(self, monkeypatch):
        # Change to /tmp so pydantic-settings can't find backend/.env
        monkeypatch.chdir("/tmp")
        monkeypatch.setenv("AGENT_MODEL", "google_genai:gemini-3.5-flash")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        import app.core.config as _config
        _config._settings_instance = None
        with pytest.raises(ConfigurationError) as exc_info:
            get_settings()
        assert "Missing API Key" in str(exc_info.value)
        assert "GOOGLE_API_KEY" in str(exc_info.value)

    def test_caches_settings_instance(self, monkeypatch):
        monkeypatch.setenv("AGENT_MODEL", "ollama:llama3")
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


class TestConfigurationError:
    def test_is_exception(self):
        assert issubclass(ConfigurationError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("test error")
