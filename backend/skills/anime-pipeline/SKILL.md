---
name: anime-live-action-pipeline
description: >-
  7-step anime-to-live-action conversion pipeline: analyze clip → design characters →
  generate references → plan shots → generate clips → review quality →
  assemble final film. Use for all anime-to-live-action generation requests.
---

# Anime to Live-Action Pipeline

## Overview

This skill provides the standard workflow for converting Japanese anime clips into cinematic live-action short films using the Deep Agents framework.

## Pipeline Steps

### Step 1: Analyze

Delegate to `analyze-agent` with the user's anime clip path and mode setting.

Pass:
- `clip_path`: Path to the input anime video
- `mode`: The execution mode (local / cloud / hybrid)

The agent returns structured data about scenes, characters, motion, and art style.

### Step 2: Design Characters

Delegate to `design-character-agent` with the analysis result from Step 1.

Pass:
- The `characters` array from the analysis
- Any `style_notes` for guidance

The agent returns detailed live-action character sheets with appearance, wardrobe, and expression sets.

### Step 3: Generate References

Delegate to `generate-reference-agent` with the character designs and style notes.

Pass:
- Character design data
- Style notes and reference prompts from the design step

The agent returns paths to generated reference images.

### Step 4: Plan Shots

Delegate to `plan-shots-agent` with the scene analysis, style notes, and reference images.

Pass:
- Scene data from the analysis (scenes array)
- Style notes
- Reference image paths

The agent returns a detailed shot plan with camera, lighting, and composition specs.

### Step 5: Generate Clips

Delegate to `generate-clips-agent` with the shot plan, references, and character designs.

Pass:
- Shot plan from Step 4
- Reference image paths
- Character design data
- Mode setting

The agent returns paths to generated video clips.

### Step 6: Review Quality

Delegate to `review-quality-agent` with the generated clip paths and original shot plan.

Pass:
- Paths to generated clips
- The original shot plan for comparison

The agent returns a quality assessment with pass/fail, score, and feedback.

**Quality Loop**: If `passed` is `False` and `iteration < max_iterations`, increment iteration and return to Step 5 with the review feedback. If `passed` is `True` or `iteration >= max_iterations`, proceed to Step 7.

### Step 7: Assemble Final (+ optional voice-over)

Delegate to `assemble-final-agent` with all approved clip paths.

Pass:
- All clip paths that passed quality review
- Desired transition type
- Optional narrator / character script

If a voice-over script is present and TTS is not `none`, call `synthesize_voiceover` then `mux_audio`. Duck native Seedance/H3 audio under the TTS track.

The agent returns the final assembled video path.

## Edge Cases

- **Invalid input**: If the user provides a non-video file or a path that doesn't exist, return an error immediately without running the pipeline.
- **Mode switching**: The mode can be changed between runs. Always use the mode the user specified.
- **Partial results**: If a step fails critically, return partial results with an error message rather than crashing.
- **Quality loop exhaustion**: If max_iterations is reached without passing quality review, proceed with the best available clips and note the quality limitation in the final output.
- **Provider down**: Tools fall back to structured mock output with `fallback: mock` and an `error` field rather than crashing the coordinator.

## Mode-Specific Notes

Slots are mix-and-match. Env `LLM_PROFILE` / `IMAGE_PROVIDER` / `VIDEO_PROVIDER` / `TTS_PROFILE` override the table.

- **local**: LLM=LM Studio (or vLLM / SGLang / Strata), image=vLLM-Omni Qwen-Image (or SGLang Diffusion / ComfyUI), video=MiniMax H3 (or LTX 2.5), TTS=Qwen3-TTS.
- **cloud**: LLM=OpenRouter, image=GPT Image 2 (Nano Banana 2 optional), video=Seedance 2.5 (OpenRouter or direct API), TTS=OpenAI speech (optional; Seedance already has native audio).
- **hybrid** (default): local LLM + local Qwen-Image + Seedance 2.5 + local Qwen3-TTS.
