# Cloud providers

Cloud slots also use HTTP. LLM chat is OpenAI-compatible. Image and video APIs differ per vendor.

## OpenRouter (default cloud LLM + default Seedance backend)

```env
LLM_PROFILE=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-sonnet-4.6
```

Hybrid **video** also uses this key when `SEEDANCE_BACKEND=openrouter` (the default).

## Seedance 2.5 (default cloud / hybrid video)

Default video provider: `seedance_2.5`. Veo is optional fallback only (`VIDEO_PROVIDER=veo`).

### OpenRouter backend (default)

```env
VIDEO_PROVIDER=seedance_2.5
SEEDANCE_BACKEND=openrouter
SEEDANCE_MODEL=bytedance/seedance-2.5
OPENROUTER_API_KEY=sk-or-...
```

The client posts chat/completions with `modalities` including video (and audio when enabled).

### Direct backend

```env
SEEDANCE_BACKEND=direct
SEEDANCE_BASE_URL=https://your-seedance-host
SEEDANCE_API_KEY=...
SEEDANCE_MODEL=seedance-2.5
```

`SEEDANCE_BASE_URL` and `SEEDANCE_API_KEY` are required. The client `POST`s `{base}/v1/videos` and polls until complete. Point `SEEDANCE_BASE_URL` at whatever official Ark / aggregator host you use.

Seedance can emit **native scene audio**. Use TTS only when you need a controlled narrator or cloned character voice (`TTS_PROFILE=none` to skip).

## GPT Image 2 (default cloud image)

```env
IMAGE_PROVIDER=gpt_image_2
OPENAI_API_KEY=...
IMAGE_MODEL=gpt-image-2
```

Best default for identity-from-reference character sheets.

## Nano Banana 2 (optional Google image)

Not required. Photoreal / cinematic stills.

```env
IMAGE_PROVIDER=nano_banana_2
GOOGLE_API_KEY=...
```

## Other cloud LLMs

```env
LLM_PROFILE=grok
XAI_API_KEY=...

LLM_PROFILE=opencode_go
OPENCODE_API_KEY=...
OPENCODE_GO_BASE_URL=https://opencode.ai/zen/v1

LLM_PROFILE=github_copilot
GITHUB_TOKEN=...
```

Copilot is token-based for now (device OAuth is a later wave).

## Cloud TTS

```env
TTS_PROFILE=openai_speech
OPENAI_API_KEY=...
```

Or disable: `TTS_PROFILE=none`.

## Hybrid live `.env` sketch

Local LM Studio + optional Omni image + Seedance on OpenRouter:

```env
DEFAULT_MODE=hybrid
MOCK_PROVIDERS=false
LLM_PROFILE=lmstudio
LLM_MODEL=your-lmstudio-id
OPENROUTER_API_KEY=sk-or-...
SEEDANCE_BACKEND=openrouter
```

If Omni is not running, send stills to the cloud:

```env
IMAGE_PROVIDER=gpt_image_2
OPENAI_API_KEY=...
TTS_PROFILE=none
```

## Fully cloud `.env` sketch

```env
DEFAULT_MODE=cloud
MOCK_PROVIDERS=false
OPENROUTER_API_KEY=...
OPENAI_API_KEY=...
```

## Outputs

Live adapters write under `backend/data/outputs/` (`references/`, `clips/`, `audio/`). Gitignored.
