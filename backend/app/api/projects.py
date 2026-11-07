from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import Asset, Conversation, Job, Message, Project
from app.db.session import get_db
from app.services.artifacts import output_path
from app.workflow.actions import apply_actions
from app.workflow.director import plan_actions
from app.workflow.jobs import run_jobs
from app.workflow.serialize import project_payload

router = APIRouter(prefix="/api")


class ProjectCreate(BaseModel):
    title: str = "Untitled short"
    mode: str = "hybrid"
    brief: str = ""


class ChatIn(BaseModel):
    content: str


class JobIn(BaseModel):
    type: str
    target_id: str = ""


def _get_project(db: Session, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "project not found")
    return project


def _conversation(db: Session, project: Project) -> Conversation:
    if project.conversations:
        return project.conversations[0]
    conv = Conversation(project_id=project.id)
    db.add(conv)
    db.flush()
    return conv


@router.post("/projects")
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(title=body.title, mode=body.mode, brief=body.brief)
    db.add(project)
    db.flush()
    db.add(Conversation(project_id=project.id))
    db.flush()
    return project_payload(project)


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    rows = db.query(Project).order_by(Project.created_at.desc()).all()
    return [{"id": p.id, "title": p.title, "status": p.status, "mode": p.mode} for p in rows]


@router.get("/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    return project_payload(_get_project(db, project_id))


@router.post("/projects/{project_id}/messages")
def post_message(project_id: str, body: ChatIn, db: Session = Depends(get_db)):
    project = _get_project(db, project_id)
    conv = _conversation(db, project)
    user_msg = Message(conversation_id=conv.id, role="user", content=body.content)
    db.add(user_msg)
    db.flush()
    empty = not project.characters and not project.scenes and not project.brief
    actions = plan_actions(body.content, is_empty_project=empty)
    jobs = apply_actions(db, project, actions)
    run_jobs(db, jobs)
    notes = [a.get("text") for a in actions if a.get("type") == "note" and a.get("text")]
    summary = f"Applied {len(actions)} action(s), ran {len(jobs)} job(s)."
    if notes:
        summary += " " + " ".join(notes)
    assistant = Message(
        conversation_id=conv.id,
        role="assistant",
        content=summary,
        actions=actions,
    )
    db.add(assistant)
    db.flush()
    return {"message": {"role": "assistant", "content": summary, "actions": actions}, "project": project_payload(project)}


@router.post("/projects/{project_id}/jobs")
def enqueue_job(project_id: str, body: JobIn, db: Session = Depends(get_db)):
    project = _get_project(db, project_id)
    job = Job(project_id=project.id, type=body.type, target_id=body.target_id, status="queued")
    db.add(job)
    db.flush()
    run_jobs(db, [job])
    return {"job": {"id": job.id, "type": job.type, "status": job.status, "error": job.error, "result": job.result}, "project": project_payload(project)}


@router.post("/projects/{project_id}/assets")
async def upload_asset(
    project_id: str,
    kind: str = "source_still",
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = _get_project(db, project_id)
    suffix = (file.filename or "upload").split(".")[-1]
    dest = output_path("uploads", project.id, f"{kind}.{suffix}")
    dest.write_bytes(await file.read())
    asset = Asset(
        project_id=project.id,
        kind=kind,
        path=str(dest),
        original_name=file.filename or "",
    )
    db.add(asset)
    db.flush()
    return {"asset": {"id": asset.id, "kind": asset.kind, "path": asset.path}, "project": project_payload(project)}
