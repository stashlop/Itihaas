"""Application factory, configuration and cross-cutting behaviour."""
import pytest

from itihaas import create_app
from itihaas.config import Config, TestingConfig

PUBLIC_PAGES = ["/", "/about", "/vlog", "/news", "/login", "/sign-up", "/guide-signup", "/shop", "/seemore"]
PROTECTED_PAGES = ["/index", "/map", "/booking", "/booking-history", "/review", "/itihaas-coins", "/cart", "/orders"]


@pytest.mark.parametrize("path", PUBLIC_PAGES)
def test_public_pages_render(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b"Itihaas" in response.data


@pytest.mark.parametrize("path", PROTECTED_PAGES)
def test_protected_pages_redirect_to_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


@pytest.mark.parametrize("path", PROTECTED_PAGES)
def test_protected_pages_render_when_logged_in(client, user, path):
    assert client.get(path).status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_html_404_page(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_api_404_is_json(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["status"] == "error"


def test_security_headers(client):
    headers = client.get("/").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "Referrer-Policy" in headers


def test_secret_key_required_in_production(monkeypatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)

    class ProductionConfig(Config):
        SECRET_KEY = None
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(ProductionConfig)


def test_postgres_url_scheme_is_normalised(monkeypatch):
    import importlib

    import itihaas.config as config_module

    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@localhost/itihaas")
    reloaded = importlib.reload(config_module)
    assert reloaded.Config.SQLALCHEMY_DATABASE_URI.startswith("postgresql://")
    monkeypatch.delenv("DATABASE_URL")
    importlib.reload(config_module)


def test_change_language(client):
    assert client.post("/change-language", json={"lang": "hi"}).status_code == 200
    assert "होम".encode() in client.get("/").data
    assert client.post("/change-language", json={"lang": "xx"}).status_code == 400


def test_static_vendor_assets_are_served(client):
    for path in ["/static/vendor/bootstrap/bootstrap.min.css", "/static/vendor/jquery/jquery.min.js",
                 "/static/css/itihaas.css", "/static/js/app.js", "/static/img/logo.svg"]:
        response = client.get(path)
        assert response.status_code == 200, path
        response.close()


def test_csrf_is_enforced_when_enabled(tmp_path):
    import re

    class CsrfConfig(TestingConfig):
        WTF_CSRF_ENABLED = True
        UPLOAD_FOLDER = str(tmp_path)

    client = create_app(CsrfConfig).test_client()
    assert client.post("/change-language", json={"lang": "hi"}).status_code == 400

    page = client.get("/").get_data(as_text=True)
    token = re.search(r'name="csrf-token" content="([^"]+)"', page).group(1)
    response = client.post("/change-language", json={"lang": "hi"}, headers={"X-CSRFToken": token})
    assert response.status_code == 200
