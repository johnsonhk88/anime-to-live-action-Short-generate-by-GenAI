# Cutting Room (frontend)

Vite + React UI for the workflow API: chat on the left, storyboard / characters / scenes / objects / VO / BGM on the right.

## Run

Backend must already be on http://127.0.0.1:8000 ([docs/01-quickstart.md](../docs/01-quickstart.md)).

```bash
cd frontend
npm install
npm run dev
```

http://localhost:5173  

`vite.config.js` proxies `/api` and `/health` to the API. If you change the API port, edit that proxy.

## Use

1. **New project**
2. Type a brief (or a change: `VO text: …`, `BGM: …`, `mix`)
3. **Regen VO audio** / **Regen BGM** / **Mix**

Uploads are API-only for now (`POST /api/projects/{id}/assets`).

## Stack

No extra UI framework. Fonts: Newsreader + IBM Plex Mono. Build: `npm run build` → `frontend/dist`.
