import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.graph import create_pipeline_agent
from app.api.projects import router as projects_router


class GenerateRequest(BaseModel):
    clip_path: str
    mode: str = "hybrid"
    max_iterations: int = 3
    voiceover_text: str = ""


pipeline_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline_agent
    from app.core.config import ConfigurationError
    from app.db.session import init_db

    init_db()
    try:
        pipeline_agent = create_pipeline_agent()
    except (ConfigurationError, Exception) as e:
        print(f"Pipeline agent not started ({e}). Workflow API still runs.", file=sys.stderr)
        pipeline_agent = None
    yield


app = FastAPI(title="Anime to Live-Action Generator", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(projects_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/health/slots")
async def health_slots():
    from app.core.config import get_settings
    from app.services.mode_factory import known_profiles, resolve_slots

    settings = get_settings()
    slots = resolve_slots(settings.default_mode)
    return {
        "status": "ok",
        "mode": settings.default_mode,
        "slots": slots.to_dict(),
        "mock_providers": settings.mock_providers,
        "seedance_backend": settings.seedance_backend,
        "known_profiles": known_profiles(),
        "pipeline_agent": pipeline_agent is not None,
    }


@app.post("/generate")
async def generate(request: GenerateRequest):
    if pipeline_agent is None:
        from fastapi import HTTPException

        raise HTTPException(503, "Coordinator not configured. Use /api/projects chat, or fix LLM keys.")
    vo = f" Voice-over: {request.voiceover_text}." if request.voiceover_text else ""
    result = pipeline_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Run the anime-to-live-action pipeline on {request.clip_path}. "
                        f"Mode: {request.mode}. Max iterations: {request.max_iterations}.{vo}"
                    ),
                }
            ],
        },
        config={"configurable": {"thread_id": "default"}},
    )
    return {"result": result["messages"][-1].content}
