# ComfyUI workflows

Used only when the **service** image/video slot is Comfy (`IMAGE_PROVIDER=comfyui` or `VIDEO_PROVIDER=minimax_h3` / `ltx_2.5`). The Cutting Room does not load these files itself.

Drop API-format workflow JSON here. The video/image clients queue them with `POST {COMFYUI_BASE_URL}/prompt`.

| File | Used by |
|------|---------|
| `txt2img.json` | `IMAGE_PROVIDER=comfyui` |
| `minimax_h3.json` | `VIDEO_PROVIDER=minimax_h3` (local live-action, default local video) |
| `ltx_2.5.json` | `VIDEO_PROVIDER=ltx_2.5` (fast local drafts) |

Export the graph from ComfyUI (API format), not the UI format.

Local image can skip Comfy entirely and use vLLM-Omni or SGLang Diffusion:

```
IMAGE_PROVIDER=vllm_omni
IMAGE_MODEL=qwen-image
VLLM_OMNI_BASE_URL=http://127.0.0.1:8091/v1
```
