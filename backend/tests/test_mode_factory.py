"""Tests for mode_factory provider resolution."""

import pytest
from app.services.mode_factory import resolve_providers, get_analysis_provider, get_image_gen_provider, get_video_gen_provider
from app.core.modes import ExecutionMode


class TestResolveProviders:
    def test_local_mode(self):
        providers = resolve_providers("local")
        assert providers == {
            "analysis": "lm_studio",
            "image_gen": "comfyui",
            "video_gen": "comfyui_video",
        }

    def test_cloud_mode(self):
        providers = resolve_providers("cloud")
        assert providers == {
            "analysis": "gemini",
            "image_gen": "gemini_imagen",
            "video_gen": "veo",
        }

    def test_hybrid_mode(self):
        providers = resolve_providers("hybrid")
        assert providers == {
            "analysis": "lm_studio",
            "image_gen": "comfyui",
            "video_gen": "veo",
        }

    def test_hybrid_is_default_for_unknown(self):
        providers = resolve_providers("unknown_mode")
        assert providers == resolve_providers("hybrid")

    def test_returns_copy_not_reference(self):
        p1 = resolve_providers("local")
        p2 = resolve_providers("local")
        assert p1 is not p2


class TestProviderGetters:
    @pytest.mark.parametrize("mode,expected", [
        ("local", "lm_studio"),
        ("cloud", "gemini"),
        ("hybrid", "lm_studio"),
    ])
    def test_analysis_provider(self, mode, expected):
        assert get_analysis_provider(mode) == expected

    @pytest.mark.parametrize("mode,expected", [
        ("local", "comfyui"),
        ("cloud", "gemini_imagen"),
        ("hybrid", "comfyui"),
    ])
    def test_image_gen_provider(self, mode, expected):
        assert get_image_gen_provider(mode) == expected

    @pytest.mark.parametrize("mode,expected", [
        ("local", "comfyui_video"),
        ("cloud", "veo"),
        ("hybrid", "veo"),
    ])
    def test_video_gen_provider(self, mode, expected):
        assert get_video_gen_provider(mode) == expected


class TestExecutionMode:
    def test_enum_values(self):
        assert ExecutionMode.LOCAL.value == "local"
        assert ExecutionMode.CLOUD.value == "cloud"
        assert ExecutionMode.HYBRID.value == "hybrid"

    def test_member_count(self):
        assert len(ExecutionMode) == 3
