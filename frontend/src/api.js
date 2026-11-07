async function req(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const api = {
  listProjects: () => req("/api/projects"),
  createProject: (body) => req("/api/projects", { method: "POST", body: JSON.stringify(body) }),
  getProject: (id) => req(`/api/projects/${id}`),
  chat: (id, content) =>
    req(`/api/projects/${id}/messages`, { method: "POST", body: JSON.stringify({ content }) }),
  job: (id, type) =>
    req(`/api/projects/${id}/jobs`, { method: "POST", body: JSON.stringify({ type }) }),
};
