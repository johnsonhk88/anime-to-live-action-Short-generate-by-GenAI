from pathlib import Path

from app.agents.state import (
    AnalysisResult,
    CharacterDesigns,
    ReferenceImages,
    ShotPlan,
    GeneratedClip,
    QualityReview,
    FinalAssembly,
)
from app.agents.tools.analysis import analyze_anime_clip, extract_frames, detect_characters
from app.agents.tools.character import design_character_sheet, generate_expression_set
from app.agents.tools.reference import generate_reference_image, style_transfer_reference
from app.agents.tools.shot_planning import plan_cinematic_shot, calculate_camera_movement
from app.agents.tools.video_generation import generate_video_clip, apply_consistent_style
from app.agents.tools.quality_review import review_video_quality, check_character_consistency
from app.agents.tools.assembly import (
    assemble_final_video,
    add_transitions,
    render_final_output,
    synthesize_voiceover,
    mux_audio,
)
from app.core.config import get_settings
from app.services.llm.model import build_chat_model
from app.services.mode_factory import resolve_slots

SKILLS_DIR = str(Path(__file__).resolve().parents[2] / "skills")

PIPELINE_COORDINATOR_PROMPT = """\
You are the Anime-to-Live-Action Pipeline Coordinator. Your job is to orchestrate the \
conversion of anime clips into cinematic live-action short films with consistent characters.

You have access to specialized subagents for each pipeline step. Always use them in order:

1. **analyze-agent** — Analyzes the anime clip to extract scenes, characters, and motion data.
2. **design-character-agent** — Designs live-action character sheets from the analysis.
3. **generate-reference-agent** — Generates reference images for characters and style.
4. **plan-shots-agent** — Plans cinematic shots based on the scene analysis and references.
5. **generate-clips-agent** — Generates video clips following the shot plan.
6. **review-quality-agent** — Reviews clip quality against the shot plan.
7. **assemble-final-agent** — Assembles clips, optional TTS voice-over, and muxes audio.

Flow rules:
- Run steps in strict order. Each step depends on the previous step's output.
- After review-quality-agent, check if quality_score >= 0.7 AND iteration < max_iterations.
  If quality is below threshold, increment iteration and loop back to generate-clips-agent.
  If max_iterations reached or quality passes, proceed to assemble-final-agent.
- Pass the mode setting (local/cloud/hybrid) through to subagents so they use the right provider.
- If voice-over is requested, call synthesize_voiceover then mux_audio after assembly.
- Seedance/H3 may already include native scene audio; duck it under TTS when both exist.

Always provide the user with the final result including the output video path and metadata.\
"""


def create_pipeline_agent(mode: str | None = None):
    from deepagents import create_deep_agent

    subagents = [
        {
            "name": "analyze-agent",
            "description": "Analyzes anime clips to extract scene information, character appearances, motion data, and style notes. Call this first.",
            "system_prompt": "You are an anime analysis specialist. Analyze the provided anime clip and return structured data about scenes, characters, motion, and style. Use the analyze_anime_clip tool as your primary analysis method, then refine with extract_frames and detect_characters.",
            "tools": [analyze_anime_clip, extract_frames, detect_characters],
            "response_format": AnalysisResult,
        },
        {
            "name": "design-character-agent",
            "description": "Designs detailed live-action character sheets from anime character analysis data. Call after analysis is complete.",
            "system_prompt": "You are a character design specialist. Transform anime character analysis into detailed live-action character designs. Use design_character_sheet for the primary design and generate_expression_set for expression references.",
            "tools": [design_character_sheet, generate_expression_set],
            "response_format": CharacterDesigns,
        },
        {
            "name": "generate-reference-agent",
            "description": "Generates reference images for characters and style transfer. Call after character designs are ready.",
            "system_prompt": "You are a reference image generation specialist. Create reference images using generate_reference_image and style_transfer_reference. Use the character designs and style notes to guide generation.",
            "tools": [generate_reference_image, style_transfer_reference],
            "response_format": ReferenceImages,
        },
        {
            "name": "plan-shots-agent",
            "description": "Plans cinematic shots with camera, lighting, and composition details. Call after references are generated.",
            "system_prompt": "You are a cinematography specialist. Plan detailed cinematic shots using plan_cinematic_shot and calculate_camera_movement. Consider the scene analysis, style notes, and reference images.",
            "tools": [plan_cinematic_shot, calculate_camera_movement],
            "response_format": ShotPlan,
        },
        {
            "name": "generate-clips-agent",
            "description": "Generates video clips following the shot plan with consistent characters. Call after shot planning.",
            "system_prompt": "You are a video generation specialist. Generate video clips using generate_video_clip and apply_consistent_style. Ensure character consistency across all clips.",
            "tools": [generate_video_clip, apply_consistent_style],
            "response_format": GeneratedClip,
        },
        {
            "name": "review-quality-agent",
            "description": "Reviews generated clip quality against the shot plan. Call after clip generation to decide if regeneration is needed.",
            "system_prompt": "You are a quality assurance specialist. Review video clip quality using review_video_quality and check_character_consistency. Return a clear pass/fail with score and detailed feedback.",
            "tools": [review_video_quality, check_character_consistency],
            "response_format": QualityReview,
        },
        {
            "name": "assemble-final-agent",
            "description": "Assembles approved clips, optional TTS voice-over, and muxes audio into the final film. Call last.",
            "system_prompt": "You are a video editing specialist. Assemble the final video using assemble_final_video, add_transitions, and render_final_output. If a voice-over script exists, call synthesize_voiceover then mux_audio.",
            "tools": [
                assemble_final_video,
                add_transitions,
                render_final_output,
                synthesize_voiceover,
                mux_audio,
            ],
            "response_format": FinalAssembly,
        },
    ]

    settings = get_settings()
    run_mode = mode or settings.default_mode
    slots = resolve_slots(run_mode)
    model = build_chat_model(run_mode)
    agent = create_deep_agent(
        model=model,
        system_prompt=(
            PIPELINE_COORDINATOR_PROMPT
            + f"\n\nActive mode: {run_mode}. Slots: llm={slots.llm}, image={slots.image}, "
            f"video={slots.video}, tts={slots.tts}."
        ),
        subagents=subagents,
        skills=[SKILLS_DIR],
        name="anime-live-action-coordinator",
    )
    return agent
