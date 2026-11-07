# Workflow product (chat + boards)

This is the **film** layer. Service adapters (LLM / image / video / TTS) sit underneath and are called from jobs.

A **project** holds:

- Chat messages (brief + “change the prompt / regen this”)
- Storyboard panels
- Characters, **scenes**, **objects**
- **VO text** and **VO audio** takes
- **BGM** cues
- Jobs and optional uploaded assets

Chat and uploads write the same records. Regenerating one VO line must not rebuild the whole film.

Project `mode=hybrid` (default) = cheap OpenRouter LLM + **local** MiniMax H3 video. Seedance is `mode=cloud` (or override `VIDEO_PROVIDER`).

SQLite default: `DATABASE_URL=sqlite:///./data/workflow.db`. Postgres: `docker compose up -d postgres`.

## Run

Terminal 1 — from `backend/`:

```bash
source .venv/bin/activate
# MOCK_PROVIDERS=true
uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
npm install && npm run dev
```

http://localhost:5173

## First-slice behavior

1. New project  
2. Chat a brief (no file required) → panels, characters, scenes, objects, VO lines, BGM cue  
3. Jobs run **in-process** on that request: VO audio (TTS tool / mock path) + BGM (silent WAV)  
4. Follow-ups (English keywords): `VO text: …`, `regen VO audio`, `BGM: taiko`, `scene`, `object` / `prop`, `mix`  
5. Mix stub: `{ clips, vo, bgm, duck_bgm_under_vo }` — real mux when clip files exist  

Upload: `POST /api/projects/{id}/assets?kind=source_still` (or `source_video`). Chat stays the director.

## Chat without the UI

```bash
ID=$(curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"Temple short","mode":"hybrid"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

curl -s -X POST http://localhost:8000/api/projects/$ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"Dark-fantasy 30s short, scarred swordsman vs temple spirit."}' | python3 -m json.tool

curl -s -X POST http://localhost:8000/api/projects/$ID/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"mix"}'
```

## Job types

| `type` | Effect |
|--------|--------|
| `regen_vo_audio` | TTS each VO line → `vo_takes` |
| `regen_bgm` | Write score WAV (silence placeholder) |
| `regen_scene_still` | Image adapter / mock path on each scene |
| `regen_object_still` | Same for props |
| `mix` | Plan: clips + VO + ducked BGM |

Prompt edits are stored on `prompt_versions` when upserts include a new prompt.

## Postgres

```bash
docker compose up -d postgres
```

```env
DATABASE_URL=postgresql+psycopg2://anime:anime@localhost:5432/anime_workflow
```

Redis in compose is for a future worker. Jobs are **not** Celery/BullMQ yet.

## Not in this slice

- Real BGM model  
- Per-panel Seedance / H3 clips  
- Lock checkboxes and inline prompt editors (use chat + regen buttons)  
- Background queue
