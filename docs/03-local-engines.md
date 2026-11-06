# Local engines

All local **LLM** engines speak OpenAI-compatible `POST {base}/chat/completions`. Image and TTS use different paths on Omni / SGLang Diffusion / Comfy. **Do not** point the chat LLM `base_url` at a diffusion-only server.

Launchers you already maintain:

- [docker-vllm-serving-engine](https://github.com/johnsonhk88/docker-vllm-serving-engine)
- [sglang-llm-inference-engine](https://github.com/johnsonhk88/sglang-llm-inference-engine)
- [strata-llm-inference-engine](https://github.com/johnsonhk88/strata-llm-inference-engine)

One GPU should not host chat + Qwen-Image + H3 + TTS at once. Give each profile its own `*_BASE_URL` (different host or port).

## Ports

| Profile | Default URL | Role |
|---------|-------------|------|
| `lmstudio` | `http://127.0.0.1:1234/v1` | Default local **LLM** |
| `vllm` | `http://127.0.0.1:8000/v1` | Text LLM |
| `vllm_omni` | `http://127.0.0.1:8091/v1` | Vision chat, **Qwen-Image**, **Qwen3-TTS** |
| `sglang` | `http://127.0.0.1:30000/v1` | Text LLM |
| `sglang_diffusion` | `http://127.0.0.1:30000/v1` | Qwen-Image / Flux (separate process from text SGLang) |
| `strata` | `http://127.0.0.1:8080/v1` | Text LLM (Bearer `STRATA_API_KEY`) |
| `ollama` | `http://127.0.0.1:11434/v1` | Text LLM |
| `comfyui` / H3 / LTX | `http://127.0.0.1:8188` | ComfyUI HTTP `/prompt` |

## LM Studio (default local LLM)

1. Load a chat model.
2. Start the local server (port 1234).
3. Confirm:

```bash
curl -s http://127.0.0.1:1234/v1/models
```

```env
LLM_PROFILE=lmstudio
LLM_MODEL=<id from /v1/models>
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
```

## vLLM (text)

```env
LLM_PROFILE=vllm
VLLM_BASE_URL=http://127.0.0.1:8000/v1
LLM_MODEL=qwen-small
```

Text vLLM is **not** Qwen-Image. For images use Omni on **8091**.

## vLLM-Omni (image + TTS + optional vision)

```env
IMAGE_PROVIDER=vllm_omni
IMAGE_MODEL=qwen-image
VLLM_OMNI_BASE_URL=http://127.0.0.1:8091/v1

TTS_PROFILE=qwen3_tts
# or TTS_PROFILE=cosyvoice3
```

Endpoints the adapters call:

- Image: `POST /v1/images/generations`
- TTS: `POST /v1/audio/speech`

Qwen3-TTS CustomVoice is the default TTS model. CosyVoice3 needs `ref_audio` + `ref_text` (clone).

## SGLang

Text:

```env
LLM_PROFILE=sglang
SGLANG_BASE_URL=http://127.0.0.1:30000/v1
LLM_MODEL=qwen-small
```

Diffusion (Qwen-Image) is a **different** server; set `SGLANG_DIFFUSION_BASE_URL` if it is not on 30000:

```env
IMAGE_PROVIDER=sglang_diffusion
IMAGE_MODEL=Qwen/Qwen-Image
```

## Strata

```env
LLM_PROFILE=strata
STRATA_BASE_URL=http://127.0.0.1:8080/v1
STRATA_API_KEY=...
```

## ComfyUI (optional image, default local video)

```env
COMFYUI_BASE_URL=http://127.0.0.1:8188
IMAGE_PROVIDER=comfyui
VIDEO_PROVIDER=minimax_h3   # or ltx_2.5
```

Drop API-format graphs in `backend/workflows/` (not the UI format):

| File | Slot |
|------|------|
| `txt2img.json` | `IMAGE_PROVIDER=comfyui` |
| `minimax_h3.json` | `VIDEO_PROVIDER=minimax_h3` |
| `ltx_2.5.json` | `VIDEO_PROVIDER=ltx_2.5` |

Those JSON files are **not in the repo yet**. Until they exist, local Comfy image/video calls fail and tools return `"fallback": "mock"`. See [`backend/workflows/README.md`](../backend/workflows/README.md).

Prefer Omni/SGLang for local stills so you can skip Comfy for image.

## Fully local `.env` sketch

```env
DEFAULT_MODE=local
MOCK_PROVIDERS=false
LLM_PROFILE=lmstudio
LLM_MODEL=your-model
IMAGE_PROVIDER=vllm_omni
IMAGE_MODEL=qwen-image
VIDEO_PROVIDER=minimax_h3
TTS_PROFILE=qwen3_tts
```
