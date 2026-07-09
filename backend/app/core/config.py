import os
from pydantic_settings import BaseSettings
from typing import Optional


MODEL_API_KEY_MAP = {
    "google_genai": "GOOGLE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "ollama": None,
    "azure_openai": "AZURE_OPENAI_API_KEY",
    "bedrock": None,
    "huggingface": "HUGGINGFACEHUB_API_TOKEN",
    "openrouter": "OPENROUTER_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "baseten": "BASETEN_API_KEY",
}

_settings_instance = None


class ConfigurationError(Exception):
    pass


class Settings(BaseSettings):
    agent_model: str = "google_genai:gemini-3.5-flash"
    default_mode: str = "hybrid"
    max_pipeline_iterations: int = 3
    langsmith_tracing: bool = False
    langsmith_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    # Local service URLs
    lm_studio_base_url: str = "http://localhost:1234/v1"
    comfyui_base_url: str = "http://localhost:8188"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is not None:
        return _settings_instance

    _settings_instance = Settings()

    provider = _settings_instance.agent_model.split(":")[0] if ":" in _settings_instance.agent_model else _settings_instance.agent_model
    env_var = MODEL_API_KEY_MAP.get(provider)
    if env_var is not None:
        api_key_attr = env_var.lower()
        if not getattr(_settings_instance, api_key_attr, None) and not os.environ.get(env_var):
            raise ConfigurationError(
                f"\n{'='*70}\n"
                f"  Missing API Key for model '{_settings_instance.agent_model}'\n"
                f"\n"
                f"  Set the {env_var} environment variable, or update AGENT_MODEL\n"
                f"  in your .env file to use a different provider.\n"
                f"\n"
                f"  Quick start:\n"
                f"    cp backend/.env.example backend/.env\n"
                f"    # Then edit backend/.env and add your API key\n"
                f"{'='*70}\n"
            )

    return _settings_instance
