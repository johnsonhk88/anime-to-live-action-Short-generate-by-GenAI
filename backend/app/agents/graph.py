def create_pipeline_agent(*args, **kwargs):
    from app.agents.pipeline import create_pipeline_agent as _create

    return _create(*args, **kwargs)


__all__ = ["create_pipeline_agent"]
