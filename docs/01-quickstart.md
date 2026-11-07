# Quickstart

Path A (mocks + UI) first. No GPU, no API keys.

## 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

In `.env`:

```env
DEFAULT_MODE=hybrid
MOCK_PROVIDERS=true
DATABASE_URL=sqlite:///./data/workflow.db
```

```bash
uvicorn app.main:app --reload --port 8000
```

http://localhost:8000/docs

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/health/slots | python3 -m json.tool
```

Hybrid slots should be `openrouter` / `vllm_omni` / `minimax_h3` / `qwen3_tts` with `mock_providers: true` (cheap online LLM + local video). That JSON is engine routing — not Gemini/Veo.

The coordinator may fail to start without an LLM; **workflow chat still works**.

## 2. Frontend (Cutting Room)

```bash
cd frontend
npm install
npm run dev
```

http://localhost:5173 — Vite proxies `/api` to `:8000`.

1. **New project**
2. Send a brief, e.g. `Dark-fantasy 30s short, scarred swordsman vs temple spirit, rain.`
3. Boards fill: storyboard, characters, scenes, objects, VO, BGM
4. Buttons: Regen VO audio · Regen BGM · Mix

Same thing via curl: [08-workflow.md](08-workflow.md).

## 3. Tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

Pytest forces mocks and a temp SQLite file.

## 4. Optional: engine smoke (not required for chat)

```bash
python3 - <<'PY'
from app.services.mode_factory import resolve_slots
from app.agents.tools.analysis import analyze_anime_clip
print(resolve_slots("hybrid").to_dict())
print(analyze_anime_clip("/tmp/anime.mp4", "hybrid")["provider"])
PY
```

## 5. Optional: Deep Agents `/generate`

Needs a live coordinator LLM (LM Studio by default). **Blocking.** Prefer the Cutting Room for day-to-day work.

```bash
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"clip_path": "/tmp/anime.mp4", "mode": "hybrid", "max_iterations": 1}'
```

503 means the agent was not built — use `/api/projects` instead.

## 6. Next

- Film objects and jobs: [08-workflow.md](08-workflow.md)
- Real Seedance / GPT Image: [04-cloud-providers.md](04-cloud-providers.md)
- Local Omni / vLLM: [03-local-engines.md](03-local-engines.md)

Notebooks in `backend/notebooks/` only probe engines. They are not the product.
