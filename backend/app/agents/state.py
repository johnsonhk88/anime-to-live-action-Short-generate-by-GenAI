from pydantic import BaseModel, Field
from typing import Optional


class PipelineState(BaseModel):
    anime_clip_path: Optional[str] = None
    analysis_result: Optional[dict] = None
    character_designs: Optional[dict] = None
    reference_images: Optional[list[str]] = None
    shot_plan: Optional[dict] = None
    generated_clips: Optional[list[str]] = None
    quality_review: Optional[dict] = None
    final_video_path: Optional[str] = None
    mode: str = Field(default="hybrid", description="local / cloud / hybrid")
    iteration: int = 0
    max_iterations: int = 3
    status: str = "pending"
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    scenes: list[dict] = Field(default_factory=list, description="Detected scenes with timestamps")
    characters: list[dict] = Field(default_factory=list, description="Detected characters with appearances")
    motion_data: dict = Field(default_factory=dict, description="Motion patterns and camera movements")
    style_notes: str = Field(default="", description="Art style and color palette observations")


class CharacterDesigns(BaseModel):
    characters: list[dict] = Field(default_factory=list, description="Character designs with appearance, expressions, outfits")


class ReferenceImages(BaseModel):
    reference_paths: list[str] = Field(default_factory=list, description="Paths to generated reference images")


class ShotPlan(BaseModel):
    shots: list[dict] = Field(default_factory=list, description="Cinematic shot list with angles, durations, descriptions")


class GeneratedClip(BaseModel):
    clip_path: str = Field(default="", description="Path to the generated video clip")
    duration: float = 0.0


class QualityReview(BaseModel):
    passed: bool = False
    score: float = 0.0
    feedback: str = ""
    issues: list[str] = Field(default_factory=list)


class FinalAssembly(BaseModel):
    final_path: str = Field(default="", description="Path to the final assembled video")
    duration: float = 0.0
    clip_count: int = 0
