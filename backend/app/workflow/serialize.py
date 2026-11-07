from __future__ import annotations

from app.db.models import Project


def _row(model, extra: dict | None = None) -> dict:
    data = {
        "id": model.id,
        "name": getattr(model, "name", None),
        "description": getattr(model, "description", None),
        "prompt": getattr(model, "prompt", None),
        "image_path": getattr(model, "image_path", None),
        "locked": getattr(model, "locked", None),
    }
    if extra:
        data.update(extra)
    return {k: v for k, v in data.items() if v is not None}


def project_payload(project: Project) -> dict:
    board = project.storyboards[0] if project.storyboards else None
    panels = []
    if board:
        panels = [
            {
                "id": p.id,
                "order": p.order,
                "caption": p.caption,
                "camera": p.camera,
                "duration": p.duration,
                "prompt": p.prompt,
                "scene": p.scene_name,
                "characters": p.character_names or [],
                "objects": p.object_names or [],
                "still_path": p.still_path,
                "clip_path": p.clip_path,
            }
            for p in sorted(board.panels, key=lambda x: x.order)
        ]
    conversation = project.conversations[0] if project.conversations else None
    messages = []
    if conversation:
        messages = [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "actions": m.actions or [],
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in sorted(conversation.messages, key=lambda x: (str(x.created_at or ""), x.id))
        ]
    return {
        "id": project.id,
        "title": project.title,
        "mode": project.mode,
        "status": project.status,
        "brief": project.brief,
        "characters": [_row(c) for c in project.characters],
        "scenes": [_row(s) for s in project.scenes],
        "objects": [_row(o) for o in project.objects],
        "panels": panels,
        "vo_lines": [
            {
                "id": v.id,
                "panel_order": v.panel_order,
                "speaker": v.speaker,
                "text": v.text,
                "emotion": v.emotion,
                "takes": [
                    {"id": t.id, "audio_path": t.audio_path, "provider": t.provider, "voice": t.voice}
                    for t in v.takes
                ],
            }
            for v in sorted(project.vo_lines, key=lambda x: (x.panel_order, x.speaker))
        ],
        "music_cues": [
            {
                "id": c.id,
                "name": c.name,
                "mood_prompt": c.mood_prompt,
                "duration": c.duration,
                "audio_path": c.audio_path,
            }
            for c in project.music_cues
        ],
        "jobs": [
            {
                "id": j.id,
                "type": j.type,
                "status": j.status,
                "error": j.error,
                "result": j.result,
            }
            for j in sorted(project.jobs, key=lambda x: (str(x.created_at or ""), x.id))
        ],
        "messages": messages,
        "assets": [{"id": a.id, "kind": a.kind, "path": a.path, "original_name": a.original_name} for a in project.assets],
    }
