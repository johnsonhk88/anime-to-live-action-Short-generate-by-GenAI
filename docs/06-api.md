# HTTP API

Base: `http://localhost:8000` · Swagger: http://localhost:8000/docs  
Cwd: `backend/` so `.env` loads.

Two surfaces:

- **Workflow** `/api/projects…` — chat, bible, jobs (the product)
- **Legacy coordinator** `POST /generate` — optional Deep Agents one-shot

---

## Workflow

CORS allows `http://localhost:5173`.

### `POST /api/projects`

```json
{ "title": "Untitled short", "mode": "hybrid", "brief": "" }
```

Returns the full project payload (empty boards).

### `GET /api/projects`

`[{ "id", "title", "status", "mode" }]`

### `GET /api/projects/{id}`

Bible: `characters`, `scenes`, `objects`, `panels`, `vo_lines` (with `takes`), `music_cues`, `jobs`, `messages`, `assets`.

404 if missing.

### `POST /api/projects/{id}/messages`

```json
{ "content": "Dark-fantasy 30s short, scarred swordsman vs temple spirit." }
```

Stores the user line, runs the director, applies actions, **runs jobs in-process**, returns `{ message, project }`.

First message on an empty project bootstraps the bible and enqueues VO + BGM jobs.

### `POST /api/projects/{id}/jobs`

```json
{ "type": "regen_vo_audio", "target_id": "" }
```

`type`: `regen_vo_audio` | `regen_bgm` | `regen_scene_still` | `regen_object_still` | `mix`

### `POST /api/projects/{id}/assets?kind=source_still`

Multipart file field `file`. `kind` examples: `source_still`, `source_video`. Saved under `data/outputs/uploads/`.

---

## Health

### `GET /health`

```json
{ "status": "ok" }
```

Does not probe engines.

### `GET /health/slots`

Default **mode** slots, `mock_providers`, Seedance backend, profile catalog, `pipeline_agent` (whether Deep Agents started).

```bash
curl -s http://localhost:8000/health/slots | python3 -m json.tool
```

---

## `POST /generate` (optional coordinator)

**Blocking** `agent.invoke`. 503 if the coordinator was not created at boot (workflow still works).

```json
{
  "clip_path": "/absolute/path/to/anime.mp4",
  "mode": "hybrid",
  "max_iterations": 3,
  "voiceover_text": ""
}
```

Missing `clip_path` → 422.

The coordinator LLM is the **default** mode’s LLM slot at process start. Restart uvicorn after changing `LLM_PROFILE` / keys / `MOCK_PROVIDERS`.
