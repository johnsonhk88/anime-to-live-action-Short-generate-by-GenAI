"""Workflow: chat → bible (scenes/objects/VO/BGM) → regen jobs."""


class TestWorkflowApi:
    def test_create_and_list_project(self, test_client):
        created = test_client.post("/api/projects", json={"title": "Temple short"}).json()
        assert created["title"] == "Temple short"
        assert created["panels"] == []
        listing = test_client.get("/api/projects").json()
        assert any(p["id"] == created["id"] for p in listing)

    def test_first_chat_bootstraps_bible(self, test_client):
        project = test_client.post("/api/projects", json={"title": "Rain"}).json()
        resp = test_client.post(
            f"/api/projects/{project['id']}/messages",
            json={"content": "Dark-fantasy 30s short, scarred swordsman vs temple spirit, rain."},
        )
        assert resp.status_code == 200
        data = resp.json()["project"]
        assert data["brief"]
        assert len(data["characters"]) >= 1
        assert len(data["scenes"]) >= 1
        assert len(data["objects"]) >= 1
        assert len(data["panels"]) >= 1
        assert len(data["vo_lines"]) >= 1
        assert len(data["music_cues"]) >= 1
        vo_jobs = [j for j in data["jobs"] if j["type"] == "regen_vo_audio"]
        bgm_jobs = [j for j in data["jobs"] if j["type"] == "regen_bgm"]
        assert vo_jobs and vo_jobs[0]["status"] == "done"
        assert bgm_jobs and bgm_jobs[0]["status"] == "done"
        assert data["music_cues"][0]["audio_path"]
        assert data["vo_lines"][0]["takes"]

    def test_followup_vo_text_and_mix(self, test_client):
        project = test_client.post("/api/projects", json={"title": "VO"}).json()
        test_client.post(
            f"/api/projects/{project['id']}/messages",
            json={"content": "A hero enters a ruined temple."},
        )
        follow = test_client.post(
            f"/api/projects/{project['id']}/messages",
            json={"content": "VO text: The rain never stops on this stone."},
        ).json()["project"]
        assert any("rain never stops" in v["text"].lower() for v in follow["vo_lines"])

        mixed = test_client.post(
            f"/api/projects/{project['id']}/jobs",
            json={"type": "mix"},
        ).json()
        assert mixed["job"]["status"] == "done"
        assert mixed["job"]["result"]["mix"]["duck_bgm_under_vo"] is True

    def test_missing_project_404(self, test_client):
        resp = test_client.get("/api/projects/not-a-real-id")
        assert resp.status_code == 404
