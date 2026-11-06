# Quickstart

Do Path A (mocks) before any GPU or API key work.

## 1. Install

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2. Dry-run (no GPUs, no keys)

In `.env`:

```env
DEFAULT_MODE=hybrid
MOCK_PROVIDERS=true
```

Start the API from `backend/`:

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/health/slots | python3 -m json.tool
```

`/health/slots` should show `mock_providers: true` and hybrid slots:

- `llm`: `lmstudio`
- `image`: `vllm_omni`
- `video`: `seedance_2.5`
- `tts`: `qwen3_tts`

That JSON is the source of truth. Do not assume Gemini or Veo.

## 3. Unit tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

Tests force `MOCK_PROVIDERS=true` and ignore `backend/.env`.

## 4. Tool-only check (no coordinator LLM)

```bash
cd backend
source .venv/bin/activate
python3 - <<'PY'
from app.services.mode_factory import resolve_slots
from app.agents.tools.analysis import analyze_anime_clip
print(resolve_slots("hybrid").to_dict())
print(analyze_anime_clip("/tmp/anime.mp4", "hybrid")["provider"])
PY
```

## 5. Full `/generate` (needs a coordinator LLM)

`POST /generate` always starts Deep Agents. Even with mocks, the **coordinator** needs a reachable OpenAI-compatible chat model (LM Studio by default).

```bash
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"clip_path": "/tmp/anime.mp4", "mode": "hybrid", "max_iterations": 1}'
```

This call is **blocking**. Keep `max_iterations` at 1 until you know the stack is healthy.

## 6. Next

- Hybrid with real Seedance: [04-cloud-providers.md](04-cloud-providers.md)
- Local engines: [03-local-engines.md](03-local-engines.md)
- OpenCode: [05-mcp.md](05-mcp.md)

Notebooks under `backend/notebooks/` are **connectivity probes** (LM Studio, Comfy, Gemini, Deep Agents). They are not the required production stack. Prefer `/health/slots` for Phase 2.
