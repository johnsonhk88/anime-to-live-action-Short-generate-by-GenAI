from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    title: Mapped[str] = mapped_column(String(200), default="Untitled")
    mode: Mapped[str] = mapped_column(String(32), default="hybrid")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    brief: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    conversations: Mapped[list[Conversation]] = relationship(back_populates="project", cascade="all, delete-orphan")
    characters: Mapped[list[Character]] = relationship(back_populates="project", cascade="all, delete-orphan")
    scenes: Mapped[list[Scene]] = relationship(back_populates="project", cascade="all, delete-orphan")
    objects: Mapped[list[Prop]] = relationship(back_populates="project", cascade="all, delete-orphan")
    storyboards: Mapped[list[Storyboard]] = relationship(back_populates="project", cascade="all, delete-orphan")
    vo_lines: Mapped[list[VoLine]] = relationship(back_populates="project", cascade="all, delete-orphan")
    music_cues: Mapped[list[MusicCue]] = relationship(back_populates="project", cascade="all, delete-orphan")
    jobs: Mapped[list[Job]] = relationship(back_populates="project", cascade="all, delete-orphan")
    prompt_versions: Mapped[list[PromptVersion]] = relationship(back_populates="project", cascade="all, delete-orphan")
    assets: Mapped[list[Asset]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    project: Mapped[Project] = relationship(back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text, default="")
    actions: Mapped[list | None] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str] = mapped_column(String(500), default="")
    locked: Mapped[str] = mapped_column(String(8), default="false")
    project: Mapped[Project] = relationship(back_populates="characters")


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str] = mapped_column(String(500), default="")
    locked: Mapped[str] = mapped_column(String(8), default="false")
    project: Mapped[Project] = relationship(back_populates="scenes")


class Prop(Base):
    __tablename__ = "props"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str] = mapped_column(String(500), default="")
    locked: Mapped[str] = mapped_column(String(8), default="false")
    project: Mapped[Project] = relationship(back_populates="objects")


class Storyboard(Base):
    __tablename__ = "storyboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    project: Mapped[Project] = relationship(back_populates="storyboards")
    panels: Mapped[list[Panel]] = relationship(back_populates="storyboard", cascade="all, delete-orphan")


class Panel(Base):
    __tablename__ = "panels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    storyboard_id: Mapped[str] = mapped_column(ForeignKey("storyboards.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=1)
    caption: Mapped[str] = mapped_column(Text, default="")
    camera: Mapped[str] = mapped_column(String(200), default="")
    duration: Mapped[float] = mapped_column(Float, default=4.0)
    prompt: Mapped[str] = mapped_column(Text, default="")
    scene_name: Mapped[str] = mapped_column(String(120), default="")
    character_names: Mapped[list | None] = mapped_column(JSON, default=list)
    object_names: Mapped[list | None] = mapped_column(JSON, default=list)
    still_path: Mapped[str] = mapped_column(String(500), default="")
    clip_path: Mapped[str] = mapped_column(String(500), default="")
    storyboard: Mapped[Storyboard] = relationship(back_populates="panels")


class VoLine(Base):
    __tablename__ = "vo_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    panel_order: Mapped[int] = mapped_column(Integer, default=1)
    speaker: Mapped[str] = mapped_column(String(80), default="narrator")
    text: Mapped[str] = mapped_column(Text, default="")
    emotion: Mapped[str] = mapped_column(String(80), default="")
    language: Mapped[str] = mapped_column(String(16), default="en")
    project: Mapped[Project] = relationship(back_populates="vo_lines")
    takes: Mapped[list[VoTake]] = relationship(back_populates="line", cascade="all, delete-orphan")


class VoTake(Base):
    __tablename__ = "vo_takes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    vo_line_id: Mapped[str] = mapped_column(ForeignKey("vo_lines.id"), index=True)
    audio_path: Mapped[str] = mapped_column(String(500), default="")
    provider: Mapped[str] = mapped_column(String(64), default="")
    voice: Mapped[str] = mapped_column(String(80), default="narrator")
    line: Mapped[VoLine] = relationship(back_populates="takes")


class MusicCue(Base):
    __tablename__ = "music_cues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), default="score")
    mood_prompt: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[float] = mapped_column(Float, default=30.0)
    audio_path: Mapped[str] = mapped_column(String(500), default="")
    duck_under_vo: Mapped[str] = mapped_column(String(8), default="true")
    project: Mapped[Project] = relationship(back_populates="music_cues")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(32))
    entity_id: Mapped[str] = mapped_column(String(36), default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    project: Mapped[Project] = relationship(back_populates="prompt_versions")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    type: Mapped[str] = mapped_column(String(64))
    target_type: Mapped[str] = mapped_column(String(32), default="")
    target_id: Mapped[str] = mapped_column(String(36), default="")
    status: Mapped[str] = mapped_column(String(24), default="queued")
    error: Mapped[str] = mapped_column(Text, default="")
    result: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    project: Mapped[Project] = relationship(back_populates="jobs")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    path: Mapped[str] = mapped_column(String(500), default="")
    original_name: Mapped[str] = mapped_column(String(255), default="")
    project: Mapped[Project] = relationship(back_populates="assets")
