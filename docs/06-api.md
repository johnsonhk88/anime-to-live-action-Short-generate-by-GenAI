# HTTP API

Base URL: `http://localhost:8000` (uvicorn). Interactive docs: http://localhost:8000/docs

The process cwd should be `backend/` so `.env` loads.

## `GET /health`

```json
{"status": "ok"}
```

Liveness only. Does not probe LM Studio or Seedance.

## `GET /health/slots`

Shows the **default mode** slots (from `.env` `DEFAULT_MODE`), mock flag, Seedance backend, and every known profile id.

```bash
curl -s http://localhost:8000/health/slots | python3 -m json.tool
```

Example shape:

```json
{
  "status": "ok",
  "mode": "hybrid",
  "slots": {
    "llm": "lmstudio",
    "image": "vllm_omni",
    "video": "seedance_2.5",
    "tts": "qwen3_tts"
  },
  "mock_providers": true,
  "seedance_backend": "openrouter",
  "known_profiles": {
    "llm": ["github_copilot", "grok", "lmstudio", "..."],
    "image": ["comfyui", "gpt_image_2", "..."],
    "video": ["ltx_2.5", "minimax_h3", "seedance_2.5", "veo"],
    "tts": ["comfy_tts", "cosyvoice3", "none", "openai_speech", "qwen3_tts"],
    "modes": ["local", "cloud", "hybrid"]
  }
}
```

`POST /generate` can still pass a different `mode` per request; that does not change this endpoint.

## `POST /generate`

**Blocking.** Starts the Deep Agents coordinator and waits for the final message.

```json
{
  "clip_path": "/absolute/path/to/anime.mp4",
  "mode": "hybrid",
  "max_iterations": 3,
  "voiceover_text": ""
}
```

| Field | Required | Default | Notes |
|-------|----------|---------|--------|
| `clip_path` | yes | | Path the analyze tool receives |
| `mode` | no | `hybrid` | `local` / `cloud` / `hybrid` |
| `max_iterations` | no | `3` | Quality-loop hint in the user message |
| `voiceover_text` | no | `""` | If set, appended to the coordinator prompt |

```bash
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "clip_path": "/data/anime.mp4",
    "mode": "hybrid",
    "max_iterations": 2,
    "voiceover_text": "The hero steps into the ruined temple."
  }'
```

Response:

```json
{"result": "<final coordinator message>"}
```

Missing `clip_path` → HTTP 422.

On startup, missing keys for the **default** mode abort the process with `pipeline agent creation failed`. Fix `.env` and restart. A request `mode` that needs extra keys is not pre-validated at boot.

## Coordinator vs tools

- Tools honor `MOCK_PROVIDERS` and the slots for the request `mode`.
- The coordinator model is built from the **default** mode’s LLM slot at process start (`create_pipeline_agent()` in lifespan). Changing only the JSON `mode` does not rebuild the coordinator LLM.

Restart uvicorn after changing `LLM_PROFILE` / keys / `MOCK_PROVIDERS`.
