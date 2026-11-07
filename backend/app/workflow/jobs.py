from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Job, MusicCue, Project, VoTake
from app.services.mode_factory import is_mock
from app.services.music.client import generate_bgm
from app.workflow.serialize import project_payload


def run_job(db: Session, job: Job) -> Job:
    project = db.get(Project, job.project_id)
    if project is None:
        job.status = "failed"
        job.error = "project missing"
        return job
    job.status = "running"
    db.flush()
    try:
        if job.type == "regen_vo_audio":
            job.result = _regen_vo(project)
        elif job.type == "regen_bgm":
            job.result = _regen_bgm(project)
        elif job.type == "regen_scene_still":
            job.result = _regen_stills(project.scenes, "scene")
        elif job.type == "regen_object_still":
            job.result = _regen_stills(project.objects, "object")
        elif job.type == "mix":
            job.result = _mix(project)
        else:
            raise RuntimeError(f"unknown job type {job.type}")
        job.status = "done"
        project.status = "ready" if job.type == "mix" else project.status
    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
    return job


def run_jobs(db: Session, jobs: list[Job]) -> None:
    for job in jobs:
        run_job(db, job)


def _regen_vo(project: Project) -> dict:
    from app.agents.tools.assembly import synthesize_voiceover

    takes = []
    mode = project.mode or "hybrid"
    for line in project.vo_lines:
        if not line.text.strip():
            continue
        result = synthesize_voiceover(line.text, voice=line.speaker, mode=mode)
        take = VoTake(
            vo_line_id=line.id,
            audio_path=result.get("audio_path") or "",
            provider=result.get("provider") or "",
            voice=line.speaker,
        )
        line.takes.append(take)
        takes.append({"line_id": line.id, "audio_path": take.audio_path, "provider": take.provider})
    return {"takes": takes, "mock": is_mock()}


def _regen_bgm(project: Project) -> dict:
    cue = project.music_cues[0] if project.music_cues else None
    if cue is None:
        cue = MusicCue(project_id=project.id, name="Score bed", mood_prompt=project.brief or "cinematic")
        project.music_cues.append(cue)
    result = generate_bgm(cue.mood_prompt or project.brief, duration=cue.duration or 30)
    cue.audio_path = result.audio_path
    return result.to_dict()


def _regen_stills(rows, kind: str) -> dict:
    from app.agents.tools.reference import generate_reference_image

    outputs = []
    for row in rows:
        prompt = row.prompt or row.name
        result = generate_reference_image(prompt, mode="hybrid")
        row.image_path = result.get("image_path") or ""
        outputs.append({"id": row.id, "kind": kind, "image_path": row.image_path})
    return {"stills": outputs}


def _mix(project: Project) -> dict:
    vo_paths = []
    for line in project.vo_lines:
        if line.takes:
            vo_paths.append(line.takes[-1].audio_path)
    bgm = project.music_cues[0].audio_path if project.music_cues else ""
    clips = []
    if project.storyboards:
        clips = [p.clip_path for p in sorted(project.storyboards[0].panels, key=lambda x: x.order) if p.clip_path]
    plan = {
        "clips": clips,
        "vo": vo_paths,
        "bgm": bgm,
        "duck_bgm_under_vo": True,
        "final_path": "/output/mix_stub.mp4" if not clips else clips[0],
        "note": "Mix stub: concat clips, lay VO, duck BGM. Real mux when clip files exist.",
    }
    return {"mix": plan, "snapshot": {"vo_count": len(vo_paths), "has_bgm": bool(bgm)}}


def snapshot(project: Project) -> dict:
    return project_payload(project)
