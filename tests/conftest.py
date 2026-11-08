"""Shared pytest fixtures: an isolated app, a client and user factories."""
from __future__ import annotations

import pytest
from werkzeug.security import generate_password_hash

from itihaas import create_app
from itihaas.config import TestingConfig
from itihaas.extensions import db as _db
from itihaas.models import Guide, User

PASSWORD = "correct-horse-1"


@pytest.fixture()
def app(tmp_path):
    class Config(TestingConfig):
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    app = create_app(Config)
    with app.app_context():
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def make_user(db):
    def _make(email="user@example.com", *, guide=False, verified=True, name="Asha"):
        user = User(email=email, first_name=name, password=generate_password_hash(PASSWORD),
                    is_verified=verified, is_guide=guide)
        db.session.add(user)
        db.session.flush()
        if guide:
            db.session.add(Guide(user_id=user.id, name=name))
        db.session.commit()
        return user

    return _make


@pytest.fixture()
def login(client):
    def _login(email="user@example.com", password=PASSWORD, **kwargs):
        return client.post("/login", data={"email": email, "password": password}, **kwargs)

    return _login


@pytest.fixture()
def user(make_user, login):
    """A verified, logged-in regular user."""
    account = make_user()
    login()
    return account
