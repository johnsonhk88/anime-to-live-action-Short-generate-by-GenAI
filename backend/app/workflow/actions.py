from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import (
    Character,
    Job,
    MusicCue,
    Panel,
    Project,
    PromptVersion,
    Prop,
    Scene,
    Storyboard,
    VoLine,
)


def _storyboard(db: Session, project: Project) -> Storyboard:
    if project.storyboards:
        return project.storyboards[0]
    board = Storyboard(project_id=project.id)
    project.storyboards.append(board)
    db.flush()
    return board


def _version(db: Session, project_id: str, entity_type: str, entity_id: str, prompt: str) -> None:
    if not prompt:
        return
    db.add(
        PromptVersion(
            project_id=project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            prompt=prompt,
        )
    )


def _upsert_named(rows, name: str):
    key = (name or "").strip().lower()
    for row in rows:
        if row.name.strip().lower() == key:
            return row
    return None


def apply_actions(db: Session, project: Project, actions: list[dict]) -> list[Job]:
    jobs: list[Job] = []
    for raw in actions:
        kind = (raw or {}).get("type")
        if kind == "set_brief":
            project.brief = raw.get("brief") or project.brief
            project.status = "developing"
        elif kind == "upsert_character":
            row = _upsert_named(project.characters, raw.get("name", "Character"))
            if row is None:
                row = Character(project_id=project.id, name=raw.get("name") or "Character")
                project.characters.append(row)
                db.flush()
            row.description = raw.get("description", row.description)
            if raw.get("prompt"):
                row.prompt = raw["prompt"]
                _version(db, project.id, "character", row.id, row.prompt)
        elif kind == "upsert_scene":
            row = _upsert_named(project.scenes, raw.get("name", "Scene"))
            if row is None:
                row = Scene(project_id=project.id, name=raw.get("name") or "Scene")
                project.scenes.append(row)
                db.flush()
            row.description = raw.get("description", row.description)
            if raw.get("prompt"):
                row.prompt = raw["prompt"]
                _version(db, project.id, "scene", row.id, row.prompt)
        elif kind == "upsert_object":
            row = _upsert_named(project.objects, raw.get("name", "Prop"))
            if row is None:
                row = Prop(project_id=project.id, name=raw.get("name") or "Prop")
                project.objects.append(row)
                db.flush()
            row.description = raw.get("description", row.description)
            if raw.get("prompt"):
                row.prompt = raw["prompt"]
                _version(db, project.id, "object", row.id, row.prompt)
        elif kind == "upsert_panel":
            board = _storyboard(db, project)
            order = int(raw.get("order") or 1)
            row = next((p for p in board.panels if p.order == order), None)
            if row is None:
                row = Panel(storyboard_id=board.id, order=order)
                board.panels.append(row)
            row.caption = raw.get("caption", row.caption)
            row.camera = raw.get("camera", row.camera)
            row.duration = float(raw.get("duration") or row.duration or 4)
            row.scene_name = raw.get("scene", row.scene_name)
            row.character_names = raw.get("characters") or row.character_names or []
            row.object_names = raw.get("objects") or row.object_names or []
            if raw.get("prompt"):
                row.prompt = raw["prompt"]
                db.flush()
                _version(db, project.id, "panel", row.id, row.prompt)
        elif kind == "upsert_vo_line":
            order = int(raw.get("panel_order") or 1)
            speaker = raw.get("speaker") or "narrator"
            row = next(
                (v for v in project.vo_lines if v.panel_order == order and v.speaker == speaker),
                None,
            )
            if row is None:
                row = VoLine(project_id=project.id, panel_order=order, speaker=speaker)
                project.vo_lines.append(row)
                db.flush()
            row.text = raw.get("text", row.text)
            row.emotion = raw.get("emotion", row.emotion)
            _version(db, project.id, "vo_text", row.id, row.text)
        elif kind == "upsert_music_cue":
            row = _upsert_named(project.music_cues, raw.get("name", "Score bed"))
            if row is None:
                row = MusicCue(project_id=project.id, name=raw.get("name") or "Score bed")
                project.music_cues.append(row)
                db.flush()
            row.mood_prompt = raw.get("mood_prompt", row.mood_prompt)
            row.duration = float(raw.get("duration") or row.duration or 30)
            _version(db, project.id, "bgm", row.id, row.mood_prompt)
        elif kind == "enqueue_job":
            job = Job(
                project_id=project.id,
                type=raw.get("job_type") or "mix",
                target_type=raw.get("target_type") or "",
                target_id=raw.get("target_id") or "",
                status="queued",
            )
            project.jobs.append(job)
            db.flush()
            jobs.append(job)
        elif kind == "note":
            continue
    db.flush()
    return jobs
