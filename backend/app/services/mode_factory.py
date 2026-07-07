from app.core.modes import ExecutionMode, MODE_CONFIGS


def resolve_providers(mode: str) -> dict:
    parsed_mode = ExecutionMode(mode)
    return MODE_CONFIGS.get(parsed_mode, MODE_CONFIGS[ExecutionMode.HYBRID]).copy()


def get_analysis_provider(mode: str) -> str:
    return resolve_providers(mode)["analysis"]


def get_image_gen_provider(mode: str) -> str:
    return resolve_providers(mode)["image_gen"]


def get_video_gen_provider(mode: str) -> str:
    return resolve_providers(mode)["video_gen"]
