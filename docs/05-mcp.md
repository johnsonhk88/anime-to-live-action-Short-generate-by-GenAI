# MCP

The pipeline is also an MCP server so OpenCode (and other agents) can call the same tools as FastAPI.

Working directory **must** be `backend/`.

## Run

```bash
cd backend
source .venv/bin/activate

python -m app.mcp_server                 # stdio (OpenCode)
python -m app.mcp_server --http --port 8100
```

HTTP bind defaults: `--host 127.0.0.1 --port 8100`.

## OpenCode (stdio)

Project or global config. Use the venv `python` if `python` is not the one with `fastmcp` installed.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "anime-pipeline": {
        "command": "python",
        "args": ["-m", "app.mcp_server"],
        "environment": {
          "MOCK_PROVIDERS": "true"
        }
      }
    }
  }
}
```

Set the MCP process cwd to `backend/` (or pass an absolute command plus `PYTHONPATH`). Live runs: drop `MOCK_PROVIDERS` and put keys in `backend/.env` as usual.

## Tools

| Tool | What it does |
|------|----------------|
| `list_slots` | Resolved llm/image/video/tts for a mode |
| `analyze_clip` | Scene / character / style JSON |
| `extract_clip_frames` | Key frames at timestamps |
| `refine_characters` | Extra character fields |
| `design_character` | Live-action sheet |
| `expression_set` | Expression prompts |
| `generate_reference` | Still via the image slot |
| `style_transfer` | Anime frame → live-action path |
| `plan_shot` | Camera / lighting plan |
| `camera_move` | Transition between shots |
| `generate_clip` | Video via the video slot |
| `restyle_clips` | Match two clips |
| `review_clip` | Quality vs shot plan |
| `character_consistency` | Identity check |
| `assemble` | Concat clips |
| `voiceover` | TTS |
| `mix_voiceover` | Mux TTS onto picture |
| `run_pipeline` | **Blocking** full Deep Agents run |

Prefer the granular tools. `run_pipeline` needs a coordinator LLM and can run for a long time.

This app also **calls** Comfy over HTTP (`/prompt`). A separate Comfy MCP process is optional; it is not required for Omni / Seedance.
