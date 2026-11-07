"""Tests for mode_factory slot resolution."""

import pytest

from app.core.modes import ExecutionMode
from app.services.mode_factory import (
    get_analysis_provider,
    get_image_gen_provider,
    get_tts_provider,
    get_video_gen_provider,
    resolve_providers,
    resolve_slots,
)


class TestResolveSlots:
    def test_local_mode(self):
        slots = resolve_slots("local")
        assert slots.to_dict() == {
            "llm": "lmstudio",
            "image": "vllm_omni",
            "video": "minimax_h3",
            "tts": "qwen3_tts",
        }

    def test_cloud_mode(self):
        slots = resolve_slots("cloud")
        assert slots.to_dict() == {
            "llm": "openrouter",
            "image": "gpt_image_2",
            "video": "seedance_2.5",
            "tts": "openai_speech",
        }

    def test_hybrid_mode(self):
        slots = resolve_slots("hybrid")
        assert slots.to_dict() == {
            "llm": "openrouter",
            "image": "vllm_omni",
            "video": "minimax_h3",
            "tts": "qwen3_tts",
        }

    def test_hybrid_is_default_for_unknown(self):
        assert resolve_slots("unknown_mode") == resolve_slots("hybrid")

    def test_resolve_providers_aliases(self):
        providers = resolve_providers("hybrid")
        assert providers["analysis"] == providers["llm"] == "openrouter"
        assert providers["image_gen"] == providers["image"] == "vllm_omni"
        assert providers["video_gen"] == providers["video"] == "minimax_h3"
        assert providers["tts"] == "qwen3_tts"


class TestProviderGetters:
    @pytest.mark.parametrize(
        "mode,expected",
        [("local", "lmstudio"), ("cloud", "openrouter"), ("hybrid", "openrouter")],
    )
    def test_analysis_provider(self, mode, expected):
        assert get_analysis_provider(mode) == expected

    @pytest.mark.parametrize(
        "mode,expected",
        [("local", "vllm_omni"), ("cloud", "gpt_image_2"), ("hybrid", "vllm_omni")],
    )
    def test_image_provider(self, mode, expected):
        assert get_image_gen_provider(mode) == expected

    @pytest.mark.parametrize(
        "mode,expected",
        [("local", "minimax_h3"), ("cloud", "seedance_2.5"), ("hybrid", "minimax_h3")],
    )
    def test_video_provider(self, mode, expected):
        assert get_video_gen_provider(mode) == expected

    @pytest.mark.parametrize(
        "mode,expected",
        [("local", "qwen3_tts"), ("cloud", "openai_speech"), ("hybrid", "qwen3_tts")],
    )
    def test_tts_provider(self, mode, expected):
        assert get_tts_provider(mode) == expected


class TestExecutionMode:
    def test_enum_values(self):
        assert ExecutionMode.LOCAL.value == "local"
        assert ExecutionMode.CLOUD.value == "cloud"
        assert ExecutionMode.HYBRID.value == "hybrid"

    def test_member_count(self):
        assert len(ExecutionMode) == 3
