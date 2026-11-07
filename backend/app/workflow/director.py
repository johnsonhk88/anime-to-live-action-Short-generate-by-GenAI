from __future__ import annotations

import json
import re

from app.services.mode_factory import is_mock


def _bootstrap(text: str) -> list[dict]:
    snippet = text.strip() or "cinematic live-action short"
    return [
        {"type": "set_brief", "brief": snippet},
        {
            "type": "upsert_character",
            "name": "Hero",
            "description": "Protagonist inferred from the brief",
            "prompt": f"cinematic live-action portrait of the hero for: {snippet[:180]}",
        },
        {
            "type": "upsert_character",
            "name": "Shadow Spirit",
            "description": "Antagonist / opposing force",
            "prompt": f"cinematic live-action antagonist for: {snippet[:180]}",
        },
        {
            "type": "upsert_scene",
            "name": "Opening location",
            "description": "Primary environment",
            "prompt": f"wide establishing live-action environment, {snippet[:180]}",
        },
        {
            "type": "upsert_object",
            "name": "Key prop",
            "description": "Signature object from the brief",
            "prompt": f"photoreal hero prop, studio lighting, {snippet[:120]}",
        },
        {
            "type": "upsert_panel",
            "order": 1,
            "caption": "Establish the world and the hero",
            "camera": "wide, slow push-in",
            "duration": 5.0,
            "scene": "Opening location",
            "characters": ["Hero"],
            "objects": ["Key prop"],
            "prompt": f"establishing shot, {snippet[:160]}",
        },
        {
            "type": "upsert_panel",
            "order": 2,
            "caption": "Confrontation",
            "camera": "medium, over-shoulder",
            "duration": 5.0,
            "scene": "Opening location",
            "characters": ["Hero", "Shadow Spirit"],
            "objects": ["Key prop"],
            "prompt": f"confrontation shot, {snippet[:160]}",
        },
        {
            "type": "upsert_vo_line",
            "panel_order": 1,
            "speaker": "narrator",
            "text": snippet if len(snippet) < 240 else snippet[:237] + "...",
            "emotion": "measured",
        },
        {
            "type": "upsert_vo_line",
            "panel_order": 2,
            "speaker": "Hero",
            "text": "We don't turn back.",
            "emotion": "determined",
        },
        {
            "type": "upsert_music_cue",
            "name": "Score bed",
            "mood_prompt": f"cinematic underscore, duck under dialogue, {snippet[:120]}",
            "duration": 30.0,
        },
    ]


def _followup(text: str) -> list[dict]:
    lower = text.lower()
    actions: list[dict] = []
    if re.search(r"\b(bgm|music|score|soundtrack)\b", lower):
        actions.append(
            {
                "type": "upsert_music_cue",
                "name": "Score bed",
                "mood_prompt": text.strip(),
                "duration": 30.0,
            }
        )
        actions.append({"type": "enqueue_job", "job_type": "regen_bgm"})
    if re.search(r"\b(vo audio|voice[- ]?over audio|tts|speak|narrat)\b", lower) and "text" not in lower:
        actions.append({"type": "enqueue_job", "job_type": "regen_vo_audio"})
    if re.search(r"\b(vo text|voice[- ]?over text|dialogue|narration|script|line)\b", lower):
        actions.append(
            {
                "type": "upsert_vo_line",
                "panel_order": 1,
                "speaker": "narrator",
                "text": text.strip(),
                "emotion": "revised",
            }
        )
    if re.search(r"\bscene\b", lower):
        actions.append(
            {
                "type": "upsert_scene",
                "name": "Revised scene",
                "description": text.strip(),
                "prompt": text.strip(),
            }
        )
        actions.append({"type": "enqueue_job", "job_type": "regen_scene_still"})
    if re.search(r"\b(object|prop)\b", lower):
        actions.append(
            {
                "type": "upsert_object",
                "name": "Revised prop",
                "description": text.strip(),
                "prompt": text.strip(),
            }
        )
        actions.append({"type": "enqueue_job", "job_type": "regen_object_still"})
    if re.search(r"\b(mix|assemble|final|mux)\b", lower):
        actions.append({"type": "enqueue_job", "job_type": "mix"})
    if re.search(r"\bcharacter\b", lower):
        actions.append(
            {
                "type": "upsert_character",
                "name": "Revised character",
                "description": text.strip(),
                "prompt": text.strip(),
            }
        )
    if not actions:
        actions.append(
            {
                "type": "upsert_vo_line",
                "panel_order": 1,
                "speaker": "narrator",
                "text": text.strip(),
                "emotion": "note",
            }
        )
        actions.append({"type": "note", "text": "Applied as VO text. Say 'regen VO audio', 'BGM', 'scene', 'object', or 'mix' for jobs."})
    return actions


def plan_actions(text: str, *, is_empty_project: bool) -> list[dict]:
    """Turn a chat message into structured workflow actions."""
    if is_empty_project:
        actions = _bootstrap(text)
        actions.append({"type": "enqueue_job", "job_type": "regen_vo_audio"})
        actions.append({"type": "enqueue_job", "job_type": "regen_bgm"})
        return actions
    if is_mock():
        return _followup(text)
    return _llm_actions(text)


def _llm_actions(text: str) -> list[dict]:
    from app.services.llm.client import get_llm_client

    schema = (
        "Return JSON {\"actions\": [...]} only. Action types: set_brief, upsert_character, "
        "upsert_scene, upsert_object, upsert_panel, upsert_vo_line, upsert_music_cue, "
        "enqueue_job (job_type: regen_vo_audio|regen_bgm|regen_scene_still|regen_object_still|mix), note."
    )
    try:
        raw = get_llm_client().chat(
            [
                {"role": "system", "content": schema},
                {"role": "user", "content": text},
            ]
        )
        start, end = raw.find("{"), raw.rfind("}")
        parsed = json.loads(raw[start : end + 1]) if start >= 0 else {}
        actions = parsed.get("actions") or []
        if actions:
            return actions
    except Exception:
        pass
    return _followup(text)
