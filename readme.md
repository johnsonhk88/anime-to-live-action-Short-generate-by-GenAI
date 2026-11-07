# anime-to-live-action-Short-generate-by-GenAI

Brief a live-action short in **chat**, lock **characters / scenes / objects / VO / BGM**, then generate clips. You can also **upload** an anime clip or stills as reference.

> **Repo**: https://github.com/johnsonhk88/anime-to-live-action-Short-generate-by-GenAI

**Status**: Workflow slice is usable with mocks (chat → bible → VO audio → BGM placeholder → mix plan). GPU/cloud engines are adapters behind that. `MOCK_PROVIDERS=true` until you wire keys.

---

## Two layers

| Layer | What it is | Where |
|-------|------------|--------|
| **Workflow (the product)** | Projects, chat, storyboard, scenes, objects, VO text/audio, BGM, mix, UI | `frontend/` + `backend/app/api/` + `backend/app/workflow/` + SQLite/Postgres |
| **Services (engines)** | OpenAI-compatible LLM, image, video, TTS, music stub | `backend/app/services/` + mode slots |

Chat and upload both write the **same** project. Regen is per asset (“rewrite VO”, “new BGM”), not one giant `/generate`.

---

## 30-second start (Cutting Room)

```bash
# API
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set MOCK_PROVIDERS=true
uvicorn app.main:app --reload --port 8000

# UI (other terminal)
cd frontend
npm install && npm run dev
```

Open **http://localhost:5173** → New project → send a brief  
e.g. `Dark-fantasy 30s short: scarred swordsman vs temple spirit, rain, 16:9.`

Then: `VO text: …` · Regen VO audio · Regen BGM · Mix.

Tests: `cd backend && pytest tests/ -v` (73+).

---

## How a film is built

```
Chat brief  and/or  upload clip / stills
        ↓
Storyboard panels
        ↓
Characters · Scenes · Objects
        ↓
VO text → VO audio (TTS)
BGM cue → score bed (placeholder WAV for now)
        ↓
Panel stills / clips (service adapters)
        ↓
Mix: picture + VO + BGM (ducked under dialogue)
```

---

## Service modes (when mocks are off)

**Hybrid** = inexpensive online LLM + **local video** (Seedance/Veo stay on `cloud` because clip APIs dominate cost).

Env `LLM_PROFILE` / `IMAGE_PROVIDER` / `VIDEO_PROVIDER` / `TTS_PROFILE` override any cell. [docs/02-modes-and-slots.md](docs/02-modes-and-slots.md)

| Mode | LLM | Image | Video | TTS |
|------|-----|-------|-------|-----|
| **local** | LM Studio | vLLM-Omni Qwen-Image | MiniMax H3 | Qwen3-TTS |
| **cloud** | OpenRouter | GPT Image 2 | Seedance 2.5 | OpenAI speech |
| **hybrid** (default) | OpenRouter (cheap LLM) | vLLM-Omni Qwen-Image | MiniMax H3 (local video) | Qwen3-TTS |

---

## Docs

| Guide | Read when |
|-------|-----------|
| [Quickstart](docs/01-quickstart.md) | Install, UI, mocks, tests |
| [Workflow](docs/08-workflow.md) | Chat, boards, jobs, SQLite/Postgres |
| [HTTP API](docs/06-api.md) | `/api/projects` and legacy `/generate` |
| [Modes and slots](docs/02-modes-and-slots.md) | Engine routing |
| [Local engines](docs/03-local-engines.md) | LM Studio, vLLM, Omni, SGLang, Strata, Comfy |
| [Cloud providers](docs/04-cloud-providers.md) | OpenRouter, Seedance, GPT Image 2 |
| [MCP](docs/05-mcp.md) | OpenCode tools |
| [Troubleshooting](docs/07-troubleshooting.md) | Keys, ports, DB, UI proxy |
| [Env](backend/.env.example) | Every variable |
| [Frontend](frontend/README.md) | Vite app |

Index: [docs/README.md](docs/README.md)

---

## Layout

```
frontend/                  Cutting Room UI (Vite + React)
backend/app/api/          workflow REST
backend/app/workflow/     chat director, jobs, mix stub
backend/app/db/            SQLAlchemy models (SQLite default)
backend/app/services/     llm / image / video / tts / music
backend/app/agents/       optional Deep Agents coordinator
docs/
docker-compose.yml         optional Postgres + Redis
```

---

## Roadmap

- **Now**: chat workflow + mock jobs; service adapters exist
- **Next**: real BGM model, per-panel Seedance, lock/edit in UI, queue (Celery or BullMQ)
- **Later**: richer uploads, checkpoints, Docker app stack

---

**Author**: Johnson (Chong Kit Sang) · [johnsonhk88](https://github.com/johnsonhk88) · Started July 2026
