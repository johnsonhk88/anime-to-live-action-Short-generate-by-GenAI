"""Tests for configuration and settings."""

import pytest

from app.core.config import ConfigurationError, Settings, get_settings, reset_settings
from app.core.profiles import LLM_PROFILES


class TestSettings:
    def test_default_values(self, monkeypatch):
        monkeypatch.delenv("DEFAULT_MODE", raising=False)
        monkeypatch.delenv("LLM_PROFILE", raising=False)
        monkeypatch.delenv("MOCK_PROVIDERS", raising=False)
        settings = Settings(_env_file=None)
        assert settings.default_mode == "hybrid"
        assert settings.max_pipeline_iterations == 3
        assert settings.mock_providers is False
        assert settings.llm_profile is None
        assert settings.seedance_backend == "openrouter"
        assert settings.langsmith_tracing is False

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("DEFAULT_MODE", "local")
        monkeypatch.setenv("MAX_PIPELINE_ITERATIONS", "5")
        monkeypatch.setenv("LLM_PROFILE", "vllm")
        monkeypatch.setenv("MOCK_PROVIDERS", "true")
        settings = Settings(_env_file=None)
        assert settings.default_mode == "local"
        assert settings.max_pipeline_iterations == 5
        assert settings.llm_profile == "vllm"
        assert settings.mock_providers is True

    def test_api_key_fields_are_optional(self, monkeypatch):
        settings = Settings(_env_file=None)
        assert settings.google_api_key is None
        assert settings.openai_api_key is None
        assert settings.openrouter_api_key is None


class TestLlmProfiles:
    def test_lmstudio_no_key_needed(self):
        assert LLM_PROFILES["lmstudio"].api_key_env is None
        assert LLM_PROFILES["vllm"].api_key_env is None
        assert LLM_PROFILES["sglang"].api_key_env is None

    def test_openrouter_needs_key(self):
        assert LLM_PROFILES["openrouter"].api_key_env == "OPENROUTER_API_KEY"

    def test_grok_needs_key(self):
        assert LLM_PROFILES["grok"].api_key_env == "XAI_API_KEY"

    def test_local_and_cloud_catalog(self):
        local = {k for k, v in LLM_PROFILES.items() if v.local}
        cloud = {k for k, v in LLM_PROFILES.items() if not v.local}
        assert {"lmstudio", "vllm", "sglang", "strata"}.issubset(local)
        assert {"openrouter", "grok", "opencode_go", "github_copilot"} == cloud


class TestGetSettings:
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        reset_settings()
        yield
        reset_settings()

    def test_local_mode_no_key_needed(self, monkeypatch):
        monkeypatch.chdir("/tmp")
        monkeypatch.setenv("DEFAULT_MODE", "local")
        monkeypatch.setenv("MOCK_PROVIDERS", "false")
        monkeypatch.delenv("LLM_PROFILE", raising=False)
        monkeypatch.delenv("IMAGE_PROVIDER", raising=False)
        monkeypatch.delenv("VIDEO_PROVIDER", raising=False)
        reset_settings()
        settings = get_settings()
        assert settings.default_mode == "local"

    def test_raises_on_missing_api_key(self, monkeypatch):
        monkeypatch.chdir("/tmp")
        monkeypatch.setenv("DEFAULT_MODE", "local")
        monkeypatch.setenv("LLM_PROFILE", "openrouter")
        monkeypatch.setenv("MOCK_PROVIDERS", "false")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        reset_settings()
        with pytest.raises(ConfigurationError) as exc_info:
            get_settings()
        assert "Missing API Key" in str(exc_info.value)
        assert "OPENROUTER_API_KEY" in str(exc_info.value)

    def test_mock_skips_key_check(self, monkeypatch):
        monkeypatch.chdir("/tmp")
        monkeypatch.setenv("DEFAULT_MODE", "cloud")
        monkeypatch.setenv("MOCK_PROVIDERS", "true")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        reset_settings()
        settings = get_settings()
        assert settings.mock_providers is True

    def test_caches_settings_instance(self, monkeypatch):
        monkeypatch.setenv("MOCK_PROVIDERS", "true")
        reset_settings()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_agent_model_alias(self, monkeypatch):
        monkeypatch.chdir("/tmp")
        monkeypatch.setenv("MOCK_PROVIDERS", "true")
        monkeypatch.setenv("AGENT_MODEL", "sglang:qwen-small")
        monkeypatch.delenv("LLM_PROFILE", raising=False)
        monkeypatch.delenv("LLM_MODEL", raising=False)
        reset_settings()
        settings = get_settings()
        assert settings.llm_profile == "sglang"
        assert settings.llm_model == "qwen-small"


class TestConfigurationError:
    def test_is_exception(self):
        assert issubclass(ConfigurationError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("test error")
