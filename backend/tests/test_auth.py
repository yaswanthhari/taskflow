def test_register_success(client):
    resp = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "pass1234",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_email(client, registered_user):
    resp = client.post("/auth/register", json={
        "email": "alice@example.com",
        "full_name": "Alice Again",
        "password": "pass1234",
    })
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_register_weak_password(client):
    resp = client.post("/auth/register", json={
        "email": "weak@example.com",
        "full_name": "Weak User",
        "password": "123",
    })
    assert resp.status_code == 422


def test_login_success(client, registered_user):
    resp = client.post("/auth/login", json={
        "email": "alice@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post("/auth/login", json={
        "email": "alice@example.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "anypass",
    })
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    resp = client.get("/projects")
    # FastAPI HTTPBearer returns 403 when Authorization header is absent
    assert resp.status_code in (401, 403)


def test_protected_route_with_invalid_token(client):
    resp = client.get("/projects", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
