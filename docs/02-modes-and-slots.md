# Modes and slots

**Service layer.** The Cutting Room ([08-workflow.md](08-workflow.md)) picks a project `mode`; these slots decide which engines jobs call.

A **mode** is only a bundle of defaults. Each run has four slots: `llm`, `image`, `video`, `tts`. Any slot can be overridden without changing mode.

```
GET /health/slots
```

## Defaults

| Mode | LLM | Image | Video | TTS |
|------|-----|-------|-------|-----|
| `local` | `lmstudio` | `vllm_omni` | `minimax_h3` | `qwen3_tts` |
| `cloud` | `openrouter` | `gpt_image_2` | `seedance_2.5` | `openai_speech` |
| `hybrid` | `openrouter` | `vllm_omni` | `minimax_h3` | `qwen3_tts` |

Unknown mode strings fall back to **hybrid**.

**Why hybrid is cheap LLM + local video:** token APIs (OpenRouter, etc.) are relatively inexpensive. Clip APIs (Seedance, Veo) are not. Hybrid keeps story/chat/prompts in the cloud and burns GPU locally for H3/LTX (or Omni stills). Use `cloud` when you want Seedance quality and will pay for it.

## Overrides

Set these in `backend/.env` (see [`.env.example`](../backend/.env.example)). Empty means “use the mode default”.

| Env | Slot | Examples |
|-----|------|----------|
| `LLM_PROFILE` | llm | `lmstudio`, `vllm`, `vllm_omni`, `sglang`, `strata`, `ollama`, `openrouter`, `grok`, `opencode_go`, `github_copilot` |
| `LLM_MODEL` | llm model id | whatever `/v1/models` returns |
| `LLM_BASE_URL` | llm URL override | `http://gpu-host:8000/v1` |
| `IMAGE_PROVIDER` | image | `vllm_omni`, `sglang_diffusion`, `comfyui`, `gpt_image_2`, `nano_banana_2` |
| `IMAGE_MODEL` | image model | `qwen-image`, `gpt-image-2` |
| `VIDEO_PROVIDER` | video | `seedance_2.5`, `minimax_h3`, `ltx_2.5`, `veo` |
| `TTS_PROFILE` | tts | `qwen3_tts`, `cosyvoice3`, `comfy_tts`, `openai_speech`, `none` |
| `TTS_ENABLED` | tts on/off | `false` forces tts slot `none` |
| `SEEDANCE_BACKEND` | Seedance transport | `openrouter` or `direct` |
| `MOCK_PROVIDERS` | skip real HTTP | `true` / `false` |

Deprecated alias: `AGENT_MODEL=sglang:qwen-small` sets `LLM_PROFILE=sglang` and `LLM_MODEL=qwen-small`.

## What each path is for

| Goal | Mode + notes |
|------|----------------|
| No network, JSON shapes | `MOCK_PROVIDERS=true` (any mode) |
| Privacy, offline | `DEFAULT_MODE=local` |
| Cheap LLM + local clips | `DEFAULT_MODE=hybrid` + `OPENROUTER_API_KEY` + MiniMax H3/LTX |
| Paid cloud video | `DEFAULT_MODE=cloud` + OpenRouter + OpenAI keys (Seedance) |
| GPT Image 2 character sheets | `IMAGE_PROVIDER=gpt_image_2` |
| Skip voice-over | `TTS_PROFILE=none` or `TTS_ENABLED=false` |
| vLLM instead of LM Studio | `LLM_PROFILE=vllm` |

## Keys required when `MOCK_PROVIDERS=false`

Only **active** slots are validated.

- `local` with defaults: no cloud keys (Strata still needs `STRATA_API_KEY` if you select it)
- `hybrid` with defaults: `OPENROUTER_API_KEY` for the LLM only. Video is local `minimax_h3`. Set `VIDEO_PROVIDER=seedance_2.5` only if you opt into cloud clips.
- `cloud` with defaults: `OPENROUTER_API_KEY` + `OPENAI_API_KEY`

Startup prints a boxed error if a required key is missing.
