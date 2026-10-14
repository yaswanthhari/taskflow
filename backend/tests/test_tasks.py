def test_create_task(client, auth_headers, project):
    pid = project["id"]
    resp = client.post(f"/projects/{pid}/tasks", json={
        "title": "Write unit tests",
        "description": "Cover all endpoints",
        "priority": "high",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Write unit tests"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


def test_list_tasks(client, auth_headers, project):
    pid = project["id"]
    client.post(f"/projects/{pid}/tasks", json={"title": "Task A"}, headers=auth_headers)
    client.post(f"/projects/{pid}/tasks", json={"title": "Task B", "status": "done"}, headers=auth_headers)
    resp = client.get(f"/projects/{pid}/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_filter_tasks_by_status(client, auth_headers, project):
    pid = project["id"]
    client.post(f"/projects/{pid}/tasks", json={"title": "Open"}, headers=auth_headers)
    client.post(f"/projects/{pid}/tasks", json={"title": "Closed", "status": "done"}, headers=auth_headers)
    resp = client.get(f"/projects/{pid}/tasks?status=done", headers=auth_headers)
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["status"] == "done"


def test_update_task_status(client, auth_headers, project):
    pid = project["id"]
    task = client.post(f"/projects/{pid}/tasks", json={"title": "My task"}, headers=auth_headers).json()
    tid = task["id"]
    resp = client.put(f"/tasks/{tid}", json={"status": "in_progress"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_delete_task(client, auth_headers, project):
    pid = project["id"]
    task = client.post(f"/projects/{pid}/tasks", json={"title": "Delete me"}, headers=auth_headers).json()
    tid = task["id"]
    resp = client.delete(f"/tasks/{tid}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/tasks/{tid}", headers=auth_headers).status_code == 404


def test_non_member_cannot_create_task(client, second_auth_headers, project):
    pid = project["id"]
    resp = client.post(f"/projects/{pid}/tasks", json={"title": "Hacked task"}, headers=second_auth_headers)
    assert resp.status_code == 403


def test_create_task_empty_title(client, auth_headers, project):
    pid = project["id"]
    resp = client.post(f"/projects/{pid}/tasks", json={"title": "   "}, headers=auth_headers)
    assert resp.status_code == 422


def test_dashboard_stats(client, auth_headers, project):
    pid = project["id"]
    client.post(f"/projects/{pid}/tasks", json={"title": "T1"}, headers=auth_headers)
    client.post(f"/projects/{pid}/tasks", json={"title": "T2", "status": "done"}, headers=auth_headers)
    resp = client.get("/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    d = resp.json()
    assert d["total_tasks"] == 2
    assert d["done"] == 1
    assert d["todo"] == 1
