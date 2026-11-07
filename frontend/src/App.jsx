import { useEffect, useState } from "react";
import { api } from "./api.js";

const TABS = ["storyboard", "characters", "scenes", "objects", "vo", "bgm"];

export default function App() {
  const [projects, setProjects] = useState([]);
  const [project, setProject] = useState(null);
  const [tab, setTab] = useState("storyboard");
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function refreshList() {
    setProjects(await api.listProjects());
  }

  async function openProject(id) {
    setProject(await api.getProject(id));
  }

  useEffect(() => {
    refreshList().catch((e) => setError(e.message));
  }, []);

  async function onCreate() {
    setBusy(true);
    setError("");
    try {
      const created = await api.createProject({ title: "New short", mode: "hybrid" });
      await refreshList();
      setProject(created);
      setDraft("Dark-fantasy 30s short: scarred swordsman vs temple spirit, rain, 16:9.");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function onSend(e) {
    e.preventDefault();
    if (!project || !draft.trim()) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.chat(project.id, draft.trim());
      setProject(result.project);
      setDraft("");
      await refreshList();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function runJob(type) {
    if (!project) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.job(project.id, type);
      setProject(result.project);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const messages = project?.messages || [];

  return (
    <div className="shell">
      <aside className="rail">
        <p className="mark">Cutting Room</p>
        <p className="sub">Anime → live action</p>
        <button className="primary" onClick={onCreate} disabled={busy}>
          New project
        </button>
        <ul className="plist">
          {projects.map((p) => (
            <li key={p.id}>
              <button
                className={project?.id === p.id ? "active" : ""}
                onClick={() => openProject(p.id)}
              >
                <span>{p.title}</span>
                <em>{p.status}</em>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="chat">
        <header>
          <h1>{project ? project.title : "No project open"}</h1>
          {project && (
            <p className="meta">
              {project.mode} · {project.status}
            </p>
          )}
        </header>
        <div className="log">
          {!project && <p className="hint">Create a project, then brief the film in the box below.</p>}
          {messages.map((m) => (
            <article key={m.id} className={m.role}>
              <span>{m.role}</span>
              <p>{m.content}</p>
            </article>
          ))}
        </div>
        <form onSubmit={onSend}>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Brief the short, or: rewrite VO, regen BGM, add a scene, mix…"
            disabled={!project || busy}
          />
          <div className="row">
            <button type="submit" disabled={!project || busy}>
              {busy ? "Working…" : "Send"}
            </button>
            {error && <small className="err">{error}</small>}
          </div>
        </form>
      </section>

      <section className="board">
        <nav>
          {TABS.map((t) => (
            <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
        </nav>
        <div className="jobs">
          <button onClick={() => runJob("regen_vo_audio")} disabled={!project || busy}>
            Regen VO audio
          </button>
          <button onClick={() => runJob("regen_bgm")} disabled={!project || busy}>
            Regen BGM
          </button>
          <button onClick={() => runJob("mix")} disabled={!project || busy}>
            Mix
          </button>
        </div>
        <Board tab={tab} project={project} />
      </section>
    </div>
  );
}

function Board({ tab, project }) {
  if (!project) return <p className="hint">Boards fill after the first brief.</p>;
  if (tab === "storyboard") {
    return (
      <ol className="cards">
        {(project.panels || []).map((p) => (
          <li key={p.id}>
            <strong>#{p.order}</strong>
            <p>{p.caption}</p>
            <small>
              {p.camera} · {p.duration}s · {p.scene}
            </small>
          </li>
        ))}
      </ol>
    );
  }
  if (tab === "characters" || tab === "scenes" || tab === "objects") {
    const rows = project[tab] || [];
    return (
      <ul className="cards">
        {rows.map((r) => (
          <li key={r.id}>
            <strong>{r.name}</strong>
            <p>{r.description}</p>
            <small>{r.prompt}</small>
          </li>
        ))}
      </ul>
    );
  }
  if (tab === "vo") {
    return (
      <ul className="cards">
        {(project.vo_lines || []).map((v) => (
          <li key={v.id}>
            <strong>
              P{v.panel_order} · {v.speaker}
            </strong>
            <p>{v.text}</p>
            <small>
              {v.emotion} · takes {v.takes?.length || 0}
              {v.takes?.[v.takes.length - 1]?.audio_path
                ? ` · ${v.takes[v.takes.length - 1].audio_path}`
                : ""}
            </small>
          </li>
        ))}
      </ul>
    );
  }
  return (
    <ul className="cards">
      {(project.music_cues || []).map((c) => (
        <li key={c.id}>
          <strong>{c.name}</strong>
          <p>{c.mood_prompt}</p>
          <small>
            {c.duration}s {c.audio_path ? `· ${c.audio_path}` : ""}
          </small>
        </li>
      ))}
      {(project.jobs || [])
        .filter((j) => j.type === "mix")
        .slice(-1)
        .map((j) => (
          <li key={j.id}>
            <strong>Last mix · {j.status}</strong>
            <pre>{JSON.stringify(j.result, null, 2)}</pre>
          </li>
        ))}
    </ul>
  );
}
