# Docs

Always run backend commands from `backend/` so `.env` and `app` resolve.

There are **two layers**:

1. **Workflow** — chat, projects, storyboard, VO, BGM ([08](08-workflow.md)). Start here if you want to make a short.
2. **Services** — which LLM/image/video/TTS engine is called ([02](02-modes-and-slots.md)–[04](04-cloud-providers.md)).

| # | Guide | Contents |
|---|-------|----------|
| 1 | [Quickstart](01-quickstart.md) | Install, Cutting Room UI, mocks, pytest |
| 2 | [Modes and slots](02-modes-and-slots.md) | local / cloud / hybrid engine defaults |
| 3 | [Local engines](03-local-engines.md) | LM Studio, vLLM, Omni, SGLang, Strata, Comfy |
| 4 | [Cloud providers](04-cloud-providers.md) | OpenRouter, Seedance, GPT Image 2, Grok |
| 5 | [MCP](05-mcp.md) | OpenCode / tool server |
| 6 | [HTTP API](06-api.md) | `/api/projects`, `/health`, `/generate` |
| 7 | [Troubleshooting](07-troubleshooting.md) | Keys, ports, DB, UI, mock fallback |
| 8 | [Workflow](08-workflow.md) | Chat, scenes, objects, VO, BGM, mix |

Env: [`backend/.env.example`](../backend/.env.example)  
UI: [`frontend/README.md`](../frontend/README.md)  
Root: [`readme.md`](../readme.md)
