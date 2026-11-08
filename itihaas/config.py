"""Application configuration.

All secrets and environment-specific values are read from environment
variables (optionally loaded from a ``.env`` file). See ``.env.example`` for
the full list.
"""
from __future__ import annotations

import os

try:
    # Load a local .env file before any setting below is evaluated. Real
    # environment variables always win over values in .env.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - python-dotenv is optional
    pass


def env_bool(name: str, default: bool = False) -> bool:
    """Interpret common truthy strings (``1``, ``true``, ``yes``, ``on``)."""
    value = os.environ.get(name)
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    """Split a comma-separated environment variable into a clean list."""
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL") or "sqlite:///database.db"  # empty value = unset
    # Some hosts (Heroku, Render) still hand out the legacy "postgres://" scheme,
    # which SQLAlchemy 2.x no longer accepts.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """Base configuration shared by every environment."""

    # --- Core -----------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Relative SQLite paths are resolved by Flask-SQLAlchemy against the
    # instance folder, i.e. <repo>/instance/database.db.
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB") or 8) * 1024 * 1024

    # --- Sessions & security -------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    # Tokens stay valid for the lifetime of the session: several pages are
    # long-lived single-page flows (booking, guide dashboard).
    WTF_CSRF_TIME_LIMIT = None

    # Comma-separated list of e-mail addresses that get access to /admin-dashboard.
    ADMIN_EMAILS = [email.lower() for email in env_list("ADMIN_EMAILS")]

    # --- E-mail (Flask-Mail) ---------------------------------------------
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    MAIL_USE_SSL = env_bool("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or os.environ.get("EMAIL_USER")
    # When e-mail is not configured, print verification codes to the server
    # log instead of failing sign-up. Only honoured in debug/testing mode.
    MAIL_DEV_LOG_CODES = env_bool("MAIL_DEV_LOG_CODES", True)

    # --- Third-party integrations (all optional) ------------------------
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
    HTTP_TIMEOUT_SECONDS = float(os.environ.get("HTTP_TIMEOUT_SECONDS") or 6)
    # WhatsApp messages use pywhatkit, which drives a desktop browser. It only
    # works on a machine with a logged-in WhatsApp Web session.
    WHATSAPP_ENABLED = env_bool("WHATSAPP_ENABLED", False)

    # --- Business rules --------------------------------------------------
    COIN_REWARD_RATE = 0.10          # 10 % of a booking is returned as coins
    MAX_VISITORS_PER_BOOKING = 50
    MAX_BOOKING_AMOUNT = 500_000     # ₹ — sanity cap for simulated payments
    MAX_CART_QUANTITY = 20


class TestingConfig(Config):
    """Configuration used by the automated test-suite."""

    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    ADMIN_EMAILS = ["admin@example.com"]
    GOOGLE_MAPS_API_KEY = ""
    OPENWEATHER_API_KEY = ""
    NEWS_API_KEY = ""
    WHATSAPP_ENABLED = False
