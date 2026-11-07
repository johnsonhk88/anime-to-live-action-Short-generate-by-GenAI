"""Tests for all 7 tool modules — validates return shapes match expected schemas."""

import pytest
import inspect


class TestAnalysisTools:
    @pytest.fixture
    def analysis(self):
        from app.agents.tools.analysis import analyze_anime_clip, extract_frames, detect_characters
        return analyze_anime_clip, extract_frames, detect_characters

    def test_analyze_anime_clip_returns_required_keys(self, analysis, sample_clip_path):
        func = analysis[0]
        result = func(clip_path=sample_clip_path, mode="hybrid")
        assert "scenes" in result
        assert "characters" in result
        assert "motion_data" in result
        assert "style_notes" in result
        assert "provider" in result

    def test_analyze_returns_non_empty_scenes(self, analysis, sample_clip_path):
        result = analysis[0](clip_path=sample_clip_path)
        assert len(result["scenes"]) > 0
        for s in result["scenes"]:
            assert "id" in s
            assert "start" in s
            assert "end" in s
            assert "description" in s

    def test_extract_frames_returns_expected_shape(self, analysis, sample_clip_path):
        func = analysis[1]
        result = func(clip_path=sample_clip_path, timestamps=[0.0, 5.0, 10.0])
        assert "frames" in result
        assert "total_frames" in result
        assert result["total_frames"] == 3
        assert "format" in result
        assert result["format"] == "png"

    def test_detect_characters_refines_data(self, analysis, sample_analysis_result):
        func = analysis[2]
        result = func(sample_analysis_result)
        assert "characters" in result
        assert len(result["characters"]) > 0
        for c in result["characters"]:
            assert "estimated_expressions" in c
            assert "confidence" in c


class TestCharacterTools:
    def test_design_character_sheet(self, sample_analysis_result):
        from app.agents.tools.character import design_character_sheet
        char_data = sample_analysis_result["characters"][0]
        result = design_character_sheet(char_data)
        assert result["name"] == "Hero"
        assert "live_action_appearance" in result
        assert "wardrobe" in result
        assert "casting_notes" in result
        assert "reference_prompts" in result

    def test_generate_expression_set(self, sample_character_design):
        from app.agents.tools.character import generate_expression_set
        result = generate_expression_set(sample_character_design)
        assert result["character"] == "Hero"
        assert "expressions" in result
        assert len(result["expressions"]) == 4
        for expr in result["expressions"]:
            assert "type" in expr
            assert "prompt" in expr


class TestReferenceTools:
    def test_generate_reference_image(self):
        from app.agents.tools.reference import generate_reference_image
        result = generate_reference_image("hero in dark temple", mode="hybrid")
        assert "prompt" in result
        assert "image_path" in result
        assert "resolution" in result
        assert "provider" in result
        assert result["resolution"] == "1024x1024"
        assert result["provider"] == "vllm_omni"

    def test_style_transfer_reference(self, sample_character_design):
        from app.agents.tools.reference import style_transfer_reference
        result = style_transfer_reference("/frames/scene1/frame_0001.png", sample_character_design)
        assert "source_frame" in result
        assert "character" in result
        assert "style_transfer_path" in result
        assert "style_preservation_score" in result
        assert 0 <= result["style_preservation_score"] <= 1.0


class TestShotPlanningTools:
    def test_plan_cinematic_shot(self):
        from app.agents.tools.shot_planning import plan_cinematic_shot
        result = plan_cinematic_shot(
            scene_description="Hero confronts spirit",
            style_notes="Dark fantasy",
            reference_images=["/refs/img1.png"]
        )
        assert "camera" in result
        assert "lighting" in result
        assert "composition" in result
        assert "duration_seconds" in result
        assert result["camera"]["angle"] == "low_angle"
        assert result["lighting"]["setup"] == "three_point"

    def test_calculate_camera_movement(self):
        from app.agents.tools.shot_planning import plan_cinematic_shot, calculate_camera_movement
        shot_a = plan_cinematic_shot("scene a", "dark", ["/refs/a.png"])
        shot_b = plan_cinematic_shot("scene b", "dark", ["/refs/b.png"])
        result = calculate_camera_movement(shot_a, shot_b)
        assert "transition_type" in result
        assert "direction" in result
        assert "duration_seconds" in result


class TestVideoGenerationTools:
    def test_generate_video_clip(self, sample_character_design):
        from app.agents.tools.shot_planning import plan_cinematic_shot
        from app.agents.tools.video_generation import generate_video_clip

        shot = plan_cinematic_shot("Hero action", "dark", ["/refs/img.png"])
        result = generate_video_clip(
            shot_plan=shot,
            reference_images=["/refs/img.png"],
            character_designs=[sample_character_design],
            mode="hybrid"
        )
        assert "clip_path" in result
        assert "duration" in result
        assert "resolution" in result
        assert result["resolution"] == "1920x1080"
        assert "fps" in result
        assert "provider" in result
        assert result["provider"] == "minimax_h3"

    def test_apply_consistent_style(self):
        from app.agents.tools.video_generation import apply_consistent_style
        result = apply_consistent_style(
            clip_a_path="/clips/shot_001.mp4",
            clip_b_path="/clips/shot_002.mp4",
            style_reference="/refs/style.png"
        )
        assert "clip_a_adjusted" in result
        assert "clip_b_adjusted" in result
        assert "style_consistency_score" in result
        assert "_styled.mp4" in result["clip_a_adjusted"]


class TestQualityReviewTools:
    @pytest.fixture
    def sample_shot_plan(self):
        from app.agents.tools.shot_planning import plan_cinematic_shot
        return plan_cinematic_shot("Test scene", "dark", ["/refs/img.png"])

    def test_review_video_quality(self, sample_shot_plan):
        from app.agents.tools.quality_review import review_video_quality
        result = review_video_quality("/clips/shot_001.mp4", sample_shot_plan)
        assert "passed" in result
        assert "score" in result
        assert "feedback" in result
        assert "issues" in result
        assert result["passed"] is True
        assert 0 <= result["score"] <= 1.0

    def test_check_character_consistency(self):
        from app.agents.tools.quality_review import check_character_consistency
        result = check_character_consistency(
            clip_path="/clips/shot_001.mp4",
            character_references=["/refs/hero.png", "/refs/spirit.png"]
        )
        assert "overall_consistency" in result
        assert "characters" in result
        assert len(result["characters"]) == 2
        for c in result["characters"]:
            assert "name" in c
            assert "consistency_score" in c


class TestAssemblyTools:
    def test_assemble_final_video(self):
        from app.agents.tools.assembly import assemble_final_video
        result = assemble_final_video(
            clip_paths=["/clips/shot_001.mp4", "/clips/shot_002.mp4"],
            transition_type="crossfade"
        )
        assert "final_path" in result
        assert "duration_seconds" in result
        assert "clip_count" in result
        assert result["clip_count"] == 2
        assert result["transitions_applied"] == "crossfade"

    def test_add_transitions(self):
        from app.agents.tools.assembly import add_transitions
        result = add_transitions("/clips/a.mp4", "/clips/b.mp4", transition="dissolve", duration=0.5)
        assert "output_path" in result
        assert "transition" in result
        assert result["transition"] == "dissolve"
        assert result["result"] == "success"

    def test_render_final_output(self):
        from app.agents.tools.assembly import render_final_output
        result = render_final_output("/output/assembled.mp4", output_format="mp4", quality="high")
        assert "output_path" in result
        assert "format" in result
        assert "quality" in result
        assert "bitrate" in result
        assert result["quality"] == "high"

    def test_synthesize_voiceover_mock(self):
        from app.agents.tools.assembly import synthesize_voiceover
        result = synthesize_voiceover("The hero enters the temple.", voice="narrator", mode="hybrid")
        assert result["provider"] == "qwen3_tts"
        assert "audio_path" in result
        assert result["text"] == "The hero enters the temple."

    def test_mux_audio_skips_missing_files(self):
        from app.agents.tools.assembly import mux_audio
        result = mux_audio("/missing.mp4", "/missing.wav")
        assert result["result"] in ("skipped", "success")
        assert "output_path" in result


class TestToolImports:
    """Verify all tools are importable from the package __init__."""

    def test_all_tools_importable(self):
        from app.agents.tools import (
            analyze_anime_clip,
            extract_frames,
            detect_characters,
            design_character_sheet,
            generate_expression_set,
            generate_reference_image,
            style_transfer_reference,
            plan_cinematic_shot,
            calculate_camera_movement,
            generate_video_clip,
            apply_consistent_style,
            review_video_quality,
            check_character_consistency,
            assemble_final_video,
            add_transitions,
            render_final_output,
        )
        assert callable(analyze_anime_clip)
        assert callable(assemble_final_video)
        assert callable(render_final_output)

    def test_all_have_docstrings(self):
        from app.agents.tools import analysis, character, reference, shot_planning, video_generation, quality_review, assembly
        modules = [analysis, character, reference, shot_planning, video_generation, quality_review, assembly]
        for mod in modules:
            for name, func in inspect.getmembers(mod, inspect.isfunction):
                # Only check functions defined in this module (not imported ones like get_analysis_provider)
                if getattr(func, "__module__", None) == mod.__name__ and not name.startswith("_"):
                    assert func.__doc__, f"{mod.__name__}.{name} is missing a docstring"
