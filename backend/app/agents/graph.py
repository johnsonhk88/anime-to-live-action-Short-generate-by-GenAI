from langgraph.graph import StateGraph, START, END
from app.agents.state import PipelineState
from app.agents.tools.analysis import analyze_anime_clip
from app.agents.tools.video_generation import generate_video_clips
# ... import other tools

def create_anime_to_live_action_graph():
    workflow = StateGraph(PipelineState)

    # Add nodes (skills)
    workflow.add_node("analyze", analyze_anime_clip)
    workflow.add_node("design_characters", design_characters_node)      # TODO
    workflow.add_node("generate_references", generate_reference_images) # TODO
    workflow.add_node("plan_shots", plan_cinematic_shots)               # TODO
    workflow.add_node("generate_clips", generate_video_clips)
    workflow.add_node("review_quality", quality_review_node)            # TODO
    workflow.add_node("assemble_final", assemble_with_revideo)          # TODO

    # Define flow with possible review loop
    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "design_characters")
    workflow.add_edge("design_characters", "generate_references")
    workflow.add_edge("generate_references", "plan_shots")
    workflow.add_edge("plan_shots", "generate_clips")
    workflow.add_edge("generate_clips", "review_quality")

    # Conditional edge for quality review loop
    workflow.add_conditional_edges(
        "review_quality",
        should_regenerate,
        {
            "regenerate": "generate_clips",
            "continue": "assemble_final"
        }
    )
    workflow.add_edge("assemble_final", END)

    return workflow.compile()