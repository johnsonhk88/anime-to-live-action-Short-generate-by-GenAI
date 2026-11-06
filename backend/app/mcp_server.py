"""MCP server for the anime-to-live-action pipeline.

Run (stdio, for OpenCode):
    cd backend && python -m app.mcp_server

HTTP (optional):
    python -m app.mcp_server --http --port 8100
"""

from __future__ import annotations

import argparse


def build_mcp():
    from fastmcp import FastMCP

    from app.agents.tools.analysis import analyze_anime_clip, extract_frames, detect_characters
    from app.agents.tools.assembly import assemble_final_video, mux_audio, synthesize_voiceover
    from app.agents.tools.character import design_character_sheet, generate_expression_set
    from app.agents.tools.quality_review import check_character_consistency, review_video_quality
    from app.agents.tools.reference import generate_reference_image, style_transfer_reference
    from app.agents.tools.shot_planning import calculate_camera_movement, plan_cinematic_shot
    from app.agents.tools.video_generation import apply_consistent_style, generate_video_clip
    from app.services.mode_factory import known_profiles, resolve_slots

    mcp = FastMCP("anime-pipeline")

    @mcp.tool
    def list_slots(mode: str = "hybrid") -> dict:
        """Show resolved llm/image/video/tts providers for a mode."""
        return {"mode": mode, "slots": resolve_slots(mode).to_dict(), "known": known_profiles()}

    @mcp.tool
    def analyze_clip(clip_path: str, mode: str = "hybrid") -> dict:
        """Analyze an anime clip into scenes, characters, and style notes."""
        return analyze_anime_clip(clip_path, mode)

    @mcp.tool
    def extract_clip_frames(clip_path: str, timestamps: list[float]) -> dict:
        """Extract key frames at timestamps."""
        return extract_frames(clip_path, timestamps)

    @mcp.tool
    def refine_characters(analysis_result: dict) -> dict:
        """Refine character detections from analysis."""
        return detect_characters(analysis_result)

    @mcp.tool
    def design_character(character_data: dict, style_notes: str = "") -> dict:
        """Design a live-action character sheet."""
        return design_character_sheet(character_data, style_notes)

    @mcp.tool
    def expression_set(character_sheet: dict) -> dict:
        """Build expression prompts for a character sheet."""
        return generate_expression_set(character_sheet)

    @mcp.tool
    def generate_reference(prompt: str, mode: str = "hybrid") -> dict:
        """Generate a character/style reference image."""
        return generate_reference_image(prompt, mode)

    @mcp.tool
    def style_transfer(anime_frame_path: str, character_design: dict) -> dict:
        """Style-transfer an anime frame toward live-action."""
        return style_transfer_reference(anime_frame_path, character_design)

    @mcp.tool
    def plan_shot(scene_description: str, style_notes: str, reference_images: list[str]) -> dict:
        """Plan a cinematic shot."""
        return plan_cinematic_shot(scene_description, style_notes, reference_images)

    @mcp.tool
    def camera_move(shot_a: dict, shot_b: dict) -> dict:
        """Calculate a camera move between two shots."""
        return calculate_camera_movement(shot_a, shot_b)

    @mcp.tool
    def generate_clip(
        shot_plan: dict,
        reference_images: list[str],
        character_designs: list[dict],
        mode: str = "hybrid",
    ) -> dict:
        """Generate a live-action video clip."""
        return generate_video_clip(shot_plan, reference_images, character_designs, mode)

    @mcp.tool
    def restyle_clips(clip_a_path: str, clip_b_path: str, style_reference: str) -> dict:
        """Match visual style across two clips."""
        return apply_consistent_style(clip_a_path, clip_b_path, style_reference)

    @mcp.tool
    def review_clip(clip_path: str, shot_plan: dict) -> dict:
        """Review clip quality against the shot plan."""
        return review_video_quality(clip_path, shot_plan)

    @mcp.tool
    def character_consistency(clip_path: str, character_references: list[str]) -> dict:
        """Check character consistency in a clip."""
        return check_character_consistency(clip_path, character_references)

    @mcp.tool
    def assemble(clip_paths: list[str], transition_type: str = "crossfade") -> dict:
        """Assemble clips into a final video."""
        return assemble_final_video(clip_paths, transition_type)

    @mcp.tool
    def voiceover(text: str, voice: str = "narrator", mode: str = "hybrid") -> dict:
        """Synthesize a voice-over line."""
        return synthesize_voiceover(text, voice=voice, mode=mode)

    @mcp.tool
    def mix_voiceover(video_path: str, voiceover_path: str, output_path: str = "") -> dict:
        """Mux TTS onto a video."""
        return mux_audio(video_path, voiceover_path, output_path=output_path)

    @mcp.tool
    def run_pipeline(clip_path: str, mode: str = "hybrid", max_iterations: int = 3) -> dict:
        """Run the full Deep Agents pipeline (blocking). Prefer MOCK_PROVIDERS for dry runs."""
        from app.agents.pipeline import create_pipeline_agent

        agent = create_pipeline_agent(mode)
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Run the anime-to-live-action pipeline on {clip_path}. "
                            f"Mode: {mode}. Max iterations: {max_iterations}."
                        ),
                    }
                ],
            },
            config={"configurable": {"thread_id": "mcp"}},
        )
        content = result["messages"][-1].content
        return {"result": content, "mode": mode, "clip_path": clip_path}

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="anime-pipeline MCP server")
    parser.add_argument("--http", action="store_true", help="Serve MCP over HTTP instead of stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8100)
    args = parser.parse_args()
    mcp = build_mcp()
    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
