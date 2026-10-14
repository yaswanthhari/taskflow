def test_create_project(client, auth_headers):
    resp = client.post("/projects", json={"name": "My Project", "description": "Desc"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Project"


def test_list_projects(client, auth_headers, project):
    resp = client.get("/projects", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Alpha Project"


def test_get_project_detail(client, auth_headers, project):
    pid = project["id"]
    resp = client.get(f"/projects/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == pid
    assert len(resp.json()["members"]) >= 1


def test_update_project(client, auth_headers, project):
    pid = project["id"]
    resp = client.put(f"/projects/{pid}", json={"name": "Renamed"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"


def test_delete_project(client, auth_headers, project):
    pid = project["id"]
    resp = client.delete(f"/projects/{pid}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/projects/{pid}", headers=auth_headers).status_code == 404


def test_non_member_cannot_access_project(client, auth_headers, second_auth_headers, project):
    pid = project["id"]
    resp = client.get(f"/projects/{pid}", headers=second_auth_headers)
    assert resp.status_code == 403


def test_add_and_remove_member(client, auth_headers, second_user, project):
    pid = project["id"]
    # Add member
    resp = client.post(f"/projects/{pid}/members",
                       json={"user_email": "bob@example.com", "role": "member"},
                       headers=auth_headers)
    assert resp.status_code == 201

    # Member can now access project
    login = client.post("/auth/login", json={"email": "bob@example.com", "password": "secret456"})
    bob_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.get(f"/projects/{pid}", headers=bob_headers)
    assert resp.status_code == 200

    # Remove member
    uid = second_user["id"]
    resp = client.delete(f"/projects/{pid}/members/{uid}", headers=auth_headers)
    assert resp.status_code == 204


def test_search_projects(client, auth_headers):
    client.post("/projects", json={"name": "Alpha Team"}, headers=auth_headers)
    client.post("/projects", json={"name": "Beta Launch"}, headers=auth_headers)
    resp = client.get("/projects?search=alpha", headers=auth_headers)
    assert resp.json()["total"] == 1
    assert "alpha" in resp.json()["items"][0]["name"].lower()
