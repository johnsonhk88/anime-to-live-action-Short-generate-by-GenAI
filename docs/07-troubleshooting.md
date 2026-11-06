# Troubleshooting

## Missing API key on startup

Boxed `ConfigurationError` naming `OPENROUTER_API_KEY` (or another env). Only **active** slots are checked.

- Hybrid default needs OpenRouter because video is Seedance. Either set the key or `VIDEO_PROVIDER=minimax_h3` / `MOCK_PROVIDERS=true`.
- Cloud default also needs `OPENAI_API_KEY` (GPT Image 2).
- `SEEDANCE_BACKEND=direct` needs `SEEDANCE_BASE_URL` and `SEEDANCE_API_KEY`.

```bash
cd backend
cp .env.example .env
# edit keys, then restart uvicorn
```

## `/health` is ok but generate fails

`/health` does not probe engines. Use `/health/slots`, then:

```bash
curl -s http://127.0.0.1:1234/v1/models     # LM Studio
curl -s http://127.0.0.1:8091/v1/models     # Omni
curl -s http://127.0.0.1:8000/v1/models     # vLLM text
```

`POST /generate` needs the coordinator LLM even when tools are mocked.

## Wrong port: text vLLM vs Omni

| Port | Profile |
|------|---------|
| 1234 | LM Studio chat |
| 8000 | vLLM **text** |
| 8091 | vLLM-**Omni** (image + TTS) |
| 30000 | SGLang text (or diffusion if that is what you launched) |
| 8080 | Strata |
| 8188 | ComfyUI |

`IMAGE_PROVIDER=vllm_omni` with `VLLM_BASE_URL` (8000) will not find `/images/generations`. Set `VLLM_OMNI_BASE_URL`.

## `"fallback": "mock"` on a live run

The adapter threw; the tool returned mock JSON plus `error`. Typical causes:

- Engine down
- Comfy workflow JSON missing (`backend/workflows/minimax_h3.json`, `ltx_2.5.json`, `txt2img.json`)
- Seedance/OpenRouter 4xx
- Image model name not loaded on Omni

## Local video / Comfy does nothing useful

Workflow JSON is not shipped. Export API format from ComfyUI into `backend/workflows/` as described in [`backend/workflows/README.md`](../backend/workflows/README.md). Until then use `VIDEO_PROVIDER=seedance_2.5` or keep mocks.

## `/generate` hangs

It is synchronous `agent.invoke`. Seedance and the 7-subagent loop can take many minutes. Use `max_iterations: 1` first. Cancel the HTTP client if needed; Celery is Phase 3.

## Tests fail with missing keys / wrong slots

Pytest chdirs to a temp dir and forces `MOCK_PROVIDERS=true`. Run from `backend/`:

```bash
pytest tests/ -v
```

Do not point pytest at a broken `venv-backend-test` (old symlink). Use `.venv`.

## MCP tools not visible in OpenCode

- cwd is `backend/`
- command uses the venv that has `fastmcp`
- `/reload` after config change
- `list_slots` is a cheap smoke tool

## Notebooks still mention Gemini / Veo

Those notebooks are optional connectivity checks. Phase 2 routing is `/health/slots` + `.env` profiles, not notebook 03.
