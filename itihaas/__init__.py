"""Itihaas — discover, book and celebrate India's heritage.

This module exposes :func:`create_app`, the Flask application factory.
"""
from __future__ import annotations

import logging
import os
import secrets
from datetime import UTC, datetime

from flask import Flask, jsonify, render_template, request, session
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from .config import Config  # also loads .env (must happen before Config is evaluated)
from .extensions import csrf, db, login_manager, mail, migrate

__all__ = ["create_app", "db"]
__version__ = "2.0.0"

log = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिंदी",
    "ta": "தமிழ்",
    "kn": "ಕನ್ನಡ",
    "mr": "मराठी",
    "gu": "ગુજરાતી",
    "bho": "भोजपुरी",
    "ml": "മലയാളം",
    "te": "తెలుగు",
}


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    _configure_logging(app)
    _ensure_secret_key(app)

    os.makedirs(app.instance_path, exist_ok=True)
    app.config.setdefault("UPLOAD_FOLDER", os.path.join(app.static_folder, "uploads"))
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_template_helpers(app)
    _register_error_handlers(app)
    _register_security_headers(app)

    from .cli import register_cli

    register_cli(app)

    with app.app_context():
        # Creates missing tables only; never alters or drops existing ones.
        db.create_all()

    _warn_about_missing_integrations(app)
    return app


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------
def _configure_logging(app: Flask) -> None:
    level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")


def _ensure_secret_key(app: Flask) -> None:
    if app.config.get("SECRET_KEY"):
        return
    if app.debug or app.testing or os.environ.get("FLASK_DEBUG") == "1":
        app.config["SECRET_KEY"] = secrets.token_hex(32)
        log.warning("SECRET_KEY is not set; using a random development key (sessions reset on restart).")
        return
    raise RuntimeError(
        "SECRET_KEY environment variable is required in production. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None


def _register_blueprints(app: Flask) -> None:
    from .api import api
    from .auth import auth
    from .chatbot import chatbot_bp
    from .merchandise import merchandise_bp
    from .views import views

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(merchandise_bp)


def _register_template_helpers(app: Flask) -> None:
    from .translations import translations

    @app.context_processor
    def inject_globals():
        lang = session.get("lang", "en")
        if lang not in translations:
            lang = "en"

        def _(key: str) -> str:
            return translations[lang].get(key, translations["en"].get(key, key))

        return {
            "_": _,
            "user": current_user,
            "current_lang": lang,
            "language_names": LANGUAGE_NAMES,
            "current_year": datetime.now(UTC).year,
            "is_admin": bool(getattr(current_user, "is_admin", False)),
        }


def _wants_json() -> bool:
    return (
        request.path.startswith(("/api/", "/chatbot/", "/guide/", "/update-coins", "/change-language"))
        or request.is_json
        or request.accept_mimetypes.best == "application/json"
    )


def _register_error_handlers(app: Flask) -> None:
    def render_error(status: int, title: str, message: str):
        if _wants_json():
            return jsonify({"status": "error", "error": message}), status
        return render_template("errors/error.html", status=status, title=title, message=message), status

    @app.errorhandler(400)
    def bad_request(error):
        return render_error(400, "Bad request", "The request could not be understood.")

    @app.errorhandler(403)
    def forbidden(error):
        return render_error(403, "Access denied", "You do not have permission to view this page.")

    @app.errorhandler(404)
    def not_found(error):
        return render_error(404, "Page not found", "The page you are looking for has moved or never existed.")

    @app.errorhandler(413)
    def too_large(error):
        limit_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return render_error(413, "File too large", f"Uploads are limited to {limit_mb} MB.")

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_error(400, "Session expired", "Your session expired. Please refresh the page and try again.")

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_error(500, "Something went wrong", "An unexpected error occurred. Please try again later.")


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(self)")
        return response


def _warn_about_missing_integrations(app: Flask) -> None:
    if app.testing:
        return
    missing = [
        name
        for name, key in (
            ("E-mail (EMAIL_USER / EMAIL_PASSWORD)", app.config.get("MAIL_PASSWORD")),
            ("Google Maps (GOOGLE_MAPS_API_KEY)", app.config.get("GOOGLE_MAPS_API_KEY")),
            ("Weather (OPENWEATHER_API_KEY)", app.config.get("OPENWEATHER_API_KEY")),
            ("News (NEWS_API_KEY)", app.config.get("NEWS_API_KEY")),
        )
        if not key
    ]
    if missing:
        log.info("Optional integrations not configured: %s", ", ".join(missing))
