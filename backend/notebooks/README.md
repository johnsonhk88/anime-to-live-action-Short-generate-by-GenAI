# Connectivity notebooks

These Jupyter notebooks probe **individual engines**. They are not the product.

- Film / chat / boards: [docs/08-workflow.md](../../docs/08-workflow.md) and http://localhost:5173  
- Engine routing: `curl -s http://localhost:8000/health/slots`

See [docs/01-quickstart.md](../../docs/01-quickstart.md).

| Notebook | Probe |
|----------|--------|
| `01_test_lm_studio.ipynb` | LM Studio `:1234` (default local LLM) |
| `02_test_comfyui.ipynb` | ComfyUI `:8188` |
| `03_test_gemini.ipynb` | Gemini — **optional**. Not required for hybrid/cloud defaults |
| `04_test_deepagents.ipynb` | Deep Agents smoke |
| `05_test_full_pipeline.ipynb` | Coordinator e2e (uses mock tools unless you change env) |

Gemini / Veo in notebook 03 do **not** mean the app is Google-locked. Cloud video default is Seedance 2.5; cloud image default is GPT Image 2.
