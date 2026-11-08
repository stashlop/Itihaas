"""Reviews, persisted comments and the third-party API proxies."""
import io

import pytest
import requests

from itihaas.models import Review, ReviewComment


def create_review(client, **overrides):
    data = {"monument_name": "Hampi", "rating": "5", "review_text": "Stunning ruins.", "tags": '["history"]'}
    data.update(overrides)
    return client.post("/api/reviews", data=data, content_type="multipart/form-data")


def test_create_review(client, user):
    response = create_review(client, photos=(io.BytesIO(b"GIF89a"), "photo.gif"))
    assert response.status_code == 200
    review = Review.query.one()
    assert review.rating == 5 and review.tags == ["history"] and len(review.photos) == 1
    assert "email" not in response.get_json()["review"]["user"]


@pytest.mark.parametrize("override", [{"rating": "9"}, {"rating": "x"}, {"review_text": ""}, {"monument_name": ""}])
def test_invalid_reviews_rejected(client, user, override):
    assert create_review(client, **override).status_code == 400


def test_comments_are_persisted(client, user):
    create_review(client)
    review_id = Review.query.one().id
    assert client.get(f"/api/reviews/{review_id}/comments").get_json() == []
    posted = client.post(f"/api/reviews/{review_id}/comments", json={"text": "  <b>Agreed!</b>  "})
    assert posted.status_code == 201
    comments = client.get(f"/api/reviews/{review_id}/comments").get_json()
    assert [c["text"] for c in comments] == ["<b>Agreed!</b>"]   # stored raw, escaped by the client
    assert ReviewComment.query.count() == 1
    assert client.post(f"/api/reviews/{review_id}/comments", json={"text": "  "}).status_code == 400
    assert client.get("/api/reviews/999/comments").status_code == 404


def test_news_unconfigured(client):
    response = client.get("/api/news")
    assert response.status_code == 503
    assert response.get_json()["configured"] is False


def test_weather_unconfigured(client):
    assert client.get("/api/weather?lat=27.1&lng=78.0").status_code == 503


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def json(self):
        return self.payload


def test_news_proxy_normalises_and_hides_key(app, client, monkeypatch):
    app.config["NEWS_API_KEY"] = "secret-key"
    calls = []

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append((url, params, headers))
        return FakeResponse({"articles": [
            {"title": "Hampi restored", "url": "https://news.example/hampi", "source": {"name": "Example"},
             "publishedAt": "2026-11-01T10:00:00Z"},
            {"title": "[Removed]", "url": "https://news.example/removed"},
            {"title": "Bad link", "url": "javascript:alert(1)"},
        ]})

    monkeypatch.setattr(requests, "get", fake_get)
    data = client.get("/api/news?q=hampi").get_json()
    assert [a["title"] for a in data["articles"]] == ["Hampi restored"]
    assert calls[0][2] == {"X-Api-Key": "secret-key"}
    assert b"secret-key" not in client.get("/api/news?q=hampi").data


def test_news_proxy_handles_upstream_failure(app, client, monkeypatch):
    app.config["NEWS_API_KEY"] = "k"

    def boom(*args, **kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(requests, "get", boom)
    assert client.get("/api/news?q=unique-failure-query").status_code == 502


def test_weather_proxy_validates_coordinates(app, client, monkeypatch):
    app.config["OPENWEATHER_API_KEY"] = "k"
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(
        {"main": {"temp": 30, "feels_like": 32, "humidity": 40}, "weather": [{"main": "Clear"}], "wind": {"speed": 2}}))
    assert client.get("/api/weather?lat=999&lng=0").status_code == 400
    data = client.get("/api/weather?lat=27.17&lng=78.04").get_json()
    assert data["main"]["temp"] == 30
