import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.store import LinkStore


@pytest.fixture
def client():
    store = LinkStore()
    app.dependency_overrides[get_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_returns_201_and_a_six_char_code(client):
    r = client.post("/links", json={"url": "https://glassflow.ai"})
    assert r.status_code == 201
    body = r.json()
    assert len(body["code"]) == 6
    assert body["url"] == "https://glassflow.ai/"
    assert "created_at" in body


def test_redirect_goes_to_the_url(client):
    code = client.post("/links", json={"url": "https://glassflow.ai"}).json()["code"]
    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "https://glassflow.ai/"


def test_unknown_code_is_404(client):
    r = client.get("/nope00", follow_redirects=False)
    assert r.status_code == 404
    assert r.json() == {"detail": "unknown code"}


def test_list_is_newest_first(client):
    first = client.post("/links", json={"url": "https://example.com/1"}).json()["code"]
    second = client.post("/links", json={"url": "https://example.com/2"}).json()["code"]
    codes = [link["code"] for link in client.get("/links").json()]
    assert codes == [second, first]


def test_invalid_url_is_422(client):
    r = client.post("/links", json={"url": "not a url"})
    assert r.status_code == 422
