import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.store import LinkStore


@pytest.fixture
def store():
    return LinkStore()


@pytest.fixture
def client(store):
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


def test_each_redirect_adds_one_click(client, store):
    code = client.post("/links", json={"url": "https://glassflow.ai"}).json()["code"]
    for _ in range(2):
        r = client.get(f"/{code}", follow_redirects=False)
        assert r.status_code == 307
    link = store.get(code)
    assert link.clicks == 2
    assert link.last_clicked_at is not None


def test_unknown_code_does_not_add_a_click(client, store):
    code = client.post("/links", json={"url": "https://glassflow.ai"}).json()["code"]
    r = client.get("/nope00", follow_redirects=False)
    assert r.status_code == 404
    assert store.get(code).clicks == 0


def test_list_items_keep_their_keys_after_clicks(client):
    code = client.post("/links", json={"url": "https://glassflow.ai"}).json()["code"]
    client.get(f"/{code}", follow_redirects=False)
    items = client.get("/links").json()
    assert len(items) == 1
    assert set(items[0]) == {"code", "url", "created_at"}


def test_stats_for_a_fresh_link(client):
    created = client.post("/links", json={"url": "https://glassflow.ai"}).json()
    r = client.get(f"/links/{created['code']}/stats")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"code", "url", "clicks", "created_at", "last_clicked_at"}
    assert body["code"] == created["code"]
    assert body["url"] == "https://glassflow.ai/"
    assert body["created_at"] == created["created_at"]
    assert body["clicks"] == 0
    assert body["last_clicked_at"] is None


def test_stats_after_two_redirects(client):
    code = client.post("/links", json={"url": "https://glassflow.ai"}).json()["code"]
    for _ in range(2):
        client.get(f"/{code}", follow_redirects=False)
    body = client.get(f"/links/{code}/stats").json()
    assert body["clicks"] == 2
    assert isinstance(body["last_clicked_at"], str)


def test_stats_for_an_unknown_code_is_404(client):
    r = client.get("/links/nope00/stats")
    assert r.status_code == 404
    assert r.json() == {"detail": "unknown code"}


def test_reading_stats_does_not_count(client, store):
    code = client.post("/links", json={"url": "https://glassflow.ai"}).json()["code"]
    for _ in range(3):
        client.get(f"/links/{code}/stats")
    assert store.get(code).clicks == 0
    assert client.get(f"/links/{code}/stats").json()["clicks"] == 0
