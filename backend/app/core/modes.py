from enum import Enum


class ExecutionMode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


MODE_CONFIGS = {
    ExecutionMode.LOCAL: {
        "analysis": "lm_studio",
        "image_gen": "comfyui",
        "video_gen": "comfyui_video",
    },
    ExecutionMode.CLOUD: {
        "analysis": "gemini",
        "image_gen": "gemini_imagen",
        "video_gen": "veo",
    },
    ExecutionMode.HYBRID: {
        "analysis": "lm_studio",
        "image_gen": "comfyui",
        "video_gen": "veo",
    },
}
