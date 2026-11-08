"""Shared helpers used across blueprints."""
from __future__ import annotations

import os
import re
import uuid
from functools import wraps
from typing import Any

from flask import abort, current_app, jsonify, url_for
from flask_login import current_user
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


def allowed_image(filename: str | None) -> bool:
    return bool(filename) and "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_image_upload(file: FileStorage | None, prefix: str = "") -> str | None:
    """Validate and store an uploaded image under ``static/uploads``.

    A random component is added to the filename so uploads never overwrite each
    other. Returns the public URL, or ``None`` if the file is missing or not an
    allowed image type.
    """
    if not file or not file.filename or not allowed_image(file.filename):
        return None
    extension = file.filename.rsplit(".", 1)[1].lower()
    stem = secure_filename(file.filename.rsplit(".", 1)[0])[:40] or "image"
    filename = f"{prefix}{uuid.uuid4().hex[:12]}_{stem}.{extension}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return url_for("static", filename=f"uploads/{filename}")


def json_error(message: str, status: int = 400, **extra: Any):
    """Uniform JSON error payload. Never pass raw exception text here."""
    payload = {"status": "error", "success": False, "error": message, **extra}
    return jsonify(payload), status


def parse_int(value: Any, default: int | None = None, *, minimum: int | None = None, maximum: int | None = None) -> int | None:
    """Parse an int, returning ``default`` when invalid or out of range."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and number < minimum:
        return default
    if maximum is not None and number > maximum:
        return default
    return number


def parse_float(value: Any, default: float | None = None, *, minimum: float | None = None, maximum: float | None = None) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number != number:  # NaN
        return default
    if minimum is not None and number < minimum:
        return default
    if maximum is not None and number > maximum:
        return default
    return number


def clean_text(value: Any, max_length: int = 500) -> str:
    """Strip and truncate free-text user input."""
    return str(value or "").strip()[:max_length]


def is_valid_email(value: str | None) -> bool:
    return bool(value) and len(value) <= 150 and bool(EMAIL_RE.match(value))


def is_valid_phone(value: str | None) -> bool:
    return bool(value) and bool(PHONE_RE.match(value))


def admin_required(view):
    """Restrict a view to users listed in ``ADMIN_EMAILS``."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapper


def current_guide():
    """Return the guide profile of the logged-in user, or ``None``."""
    from .models import Guide

    if not current_user.is_authenticated or not current_user.is_guide:
        return None
    return Guide.query.filter_by(user_id=current_user.id).first()
