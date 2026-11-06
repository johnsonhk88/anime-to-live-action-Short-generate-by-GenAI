# Docs

How to run the anime-to-live-action pipeline after Phase 2 (capability slots).

Always run backend commands from `backend/` so `.env` and the `app` package resolve.

| # | Guide | Contents |
|---|-------|----------|
| 1 | [Quickstart](01-quickstart.md) | Install, mock dry-run, pytest, first generate |
| 2 | [Modes and slots](02-modes-and-slots.md) | local / cloud / hybrid defaults and env overrides |
| 3 | [Local engines](03-local-engines.md) | LM Studio, vLLM, Omni, SGLang, Strata, ComfyUI |
| 4 | [Cloud providers](04-cloud-providers.md) | OpenRouter, Seedance, GPT Image 2, Nano Banana 2, Grok |
| 5 | [MCP](05-mcp.md) | stdio/HTTP server and OpenCode config |
| 6 | [HTTP API](06-api.md) | `/health`, `/health/slots`, `/generate` |
| 7 | [Troubleshooting](07-troubleshooting.md) | Keys, ports, missing Comfy JSON, blocking generate |

Env reference (do not duplicate here): [`backend/.env.example`](../backend/.env.example).

Root overview: [`readme.md`](../readme.md).
