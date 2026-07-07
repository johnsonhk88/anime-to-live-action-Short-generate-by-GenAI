import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel

from app.agents.graph import create_pipeline_agent


class GenerateRequest(BaseModel):
    clip_path: str
    mode: str = "hybrid"
    max_iterations: int = 3


pipeline_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline_agent
    from app.core.config import ConfigurationError
    try:
        pipeline_agent = create_pipeline_agent()
    except ConfigurationError as e:
        print(str(e), file=sys.stderr)
        print("Fix the configuration above and restart the server.\n", file=sys.stderr)
        raise RuntimeError("pipeline agent creation failed")
    yield


app = FastAPI(title="Anime to Live-Action Generator", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/generate")
async def generate(request: GenerateRequest):
    result = pipeline_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Run the anime-to-live-action pipeline on {request.clip_path}. "
                        f"Mode: {request.mode}. Max iterations: {request.max_iterations}."
                    ),
                }
            ],
        },
        config={"configurable": {"thread_id": "default"}},
    )
    return {"result": result["messages"][-1].content}
