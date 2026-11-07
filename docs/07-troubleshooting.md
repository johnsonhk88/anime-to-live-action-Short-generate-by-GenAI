# Troubleshooting

## Missing API key

Boxed `ConfigurationError` for an **active** slot. Workflow chat with `MOCK_PROVIDERS=true` does not need cloud keys.

- Hybrid live → `OPENROUTER_API_KEY` for the **LLM** only; video defaults to local H3
- Cloud video / opt-in Seedance → `VIDEO_PROVIDER=seedance_2.5` plus that same OpenRouter key (or direct Seedance keys)
- Cloud image → `OPENAI_API_KEY`
- Direct Seedance → `SEEDANCE_BASE_URL` + `SEEDANCE_API_KEY`

The API **still starts** if the Deep Agents coordinator fails; `/generate` then returns 503. Use `/api/projects` / the UI.

## UI cannot reach the API

- API on `:8000`, UI `npm run dev` on `:5173`
- Proxy is in `frontend/vite.config.js`
- Browser should call `/api/projects` on 5173, not 8000, unless you set CORS and hit the API directly

## Empty boards after chat

First message only bootstraps if the project has no characters/scenes/brief. Use **New project**, then one brief. Check `GET /api/projects/{id}`.

## SQLite / Postgres

Default file: `backend/data/workflow.db` (cwd must be `backend/`).  
Postgres: `docker compose up -d postgres` and `DATABASE_URL=postgresql+psycopg2://anime:anime@localhost:5432/anime_workflow`. Restart uvicorn after changing the URL (tables `create_all` on boot; no Alembic yet).

## `/health` ok but `/generate` fails

`/health` does not probe engines. `/health/slots` → `pipeline_agent`. Coordinator needs LM Studio (or your LLM profile):

```bash
curl -s http://127.0.0.1:1234/v1/models
curl -s http://127.0.0.1:8091/v1/models
curl -s http://127.0.0.1:8000/v1/models
```

## Wrong port: text vLLM vs Omni

| Port | Profile |
|------|---------|
| 1234 | LM Studio chat |
| 8000 | vLLM **text** |
| 8091 | vLLM-**Omni** (image + TTS) |
| 30000 | SGLang |
| 8080 | Strata |
| 8188 | ComfyUI |
| 5173 | Cutting Room UI |
| 5432 | optional Postgres |

`IMAGE_PROVIDER=vllm_omni` needs `VLLM_OMNI_BASE_URL`, not `VLLM_BASE_URL`.

## `"fallback": "mock"` on a live tool call

Adapter error: engine down, missing Comfy JSON, Seedance 4xx, wrong Omni model name.

## Local Comfy video

No workflow JSON is shipped. See [`backend/workflows/README.md`](../backend/workflows/README.md). Use Seedance or mocks until then.

## `/generate` hangs

Synchronous coordinator. Use `max_iterations: 1` or skip it and stay on workflow chat. Queue is not wired yet.

## Tests

```bash
cd backend && pytest tests/ -v
```

Uses temp SQLite + mocks. Ignore `venv-backend-test`; use `.venv`.

## MCP

cwd `backend/`, venv has `fastmcp`, `/reload` in OpenCode. Smoke: `list_slots`.

## Notebooks mention Gemini / Veo

Optional probes only. Product routing is `/health/slots` + workflow projects.
