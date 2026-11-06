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

__all__ = [
    "analyze_anime_clip",
    "extract_frames",
    "detect_characters",
    "design_character_sheet",
    "generate_expression_set",
    "generate_reference_image",
    "style_transfer_reference",
    "plan_cinematic_shot",
    "calculate_camera_movement",
    "generate_video_clip",
    "apply_consistent_style",
    "review_video_quality",
    "check_character_consistency",
    "assemble_final_video",
    "add_transitions",
    "render_final_output",
    "synthesize_voiceover",
    "mux_audio",
]
