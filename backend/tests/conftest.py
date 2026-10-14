import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_taskflow.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    resp = client.post("/auth/register", json={
        "email": "alice@example.com",
        "full_name": "Alice Smith",
        "password": "secret123",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def auth_headers(client, registered_user):
    resp = client.post("/auth/login", json={
        "email": "alice@example.com",
        "password": "secret123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(client):
    resp = client.post("/auth/register", json={
        "email": "bob@example.com",
        "full_name": "Bob Jones",
        "password": "secret456",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def second_auth_headers(client, second_user):
    resp = client.post("/auth/login", json={
        "email": "bob@example.com",
        "password": "secret456",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def project(client, auth_headers):
    resp = client.post("/projects", json={"name": "Alpha Project", "description": "Test project"}, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()
