from app.core.modes import ExecutionMode, MODE_CONFIGS


def resolve_providers(mode: str) -> dict:
    """Resolve provider config for a given mode string (local/cloud/hybrid). Falls back to hybrid for unknown values."""
    try:
        parsed_mode = ExecutionMode(mode)
    except ValueError:
        parsed_mode = ExecutionMode.HYBRID
    return MODE_CONFIGS.get(parsed_mode, MODE_CONFIGS[ExecutionMode.HYBRID]).copy()


def get_analysis_provider(mode: str) -> str:
    return resolve_providers(mode)["analysis"]


def get_image_gen_provider(mode: str) -> str:
    return resolve_providers(mode)["image_gen"]


def get_video_gen_provider(mode: str) -> str:
    return resolve_providers(mode)["video_gen"]
