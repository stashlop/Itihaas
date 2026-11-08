"""Authentication: sign-up, e-mail verification, login and logout."""
from __future__ import annotations

import logging
from urllib.parse import urlsplit

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .data.heritage import HERITAGE_SITES
from .email_utils import send_verification_email
from .extensions import db
from .models import Guide, GuideDetails, User
from .utils import clean_text, is_valid_email, is_valid_phone, parse_int

auth = Blueprint("auth", __name__)
log = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 8


def _safe_next_url(target: str | None) -> str | None:
    """Only allow relative redirects back into this site."""
    if not target:
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    return target


def _home_for(user: User) -> str:
    if user.is_admin:
        return url_for("views.admin_dashboard")
    if user.is_guide:
        return url_for("views.guide_dashboard")
    return url_for("views.home")


def _validate_signup(form) -> tuple[dict, list[str]]:
    data = {
        "email": clean_text(form.get("email"), 150).lower(),
        "first_name": clean_text(form.get("firstName"), 150),
        "password1": form.get("password1") or "",
        "password2": form.get("password2") or "",
        "phone": clean_text(form.get("phone"), 20),
    }
    errors = []
    if not is_valid_email(data["email"]):
        errors.append("Please enter a valid e-mail address.")
    elif User.query.filter(db.func.lower(User.email) == data["email"]).first():
        errors.append("An account with this e-mail already exists.")
    if len(data["first_name"]) < 2:
        errors.append("First name must be at least 2 characters.")
    if len(data["password1"]) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    elif data["password1"] != data["password2"]:
        errors.append("Passwords don't match.")
    return data, errors


def _start_verification(user: User) -> bool:
    """Generate a code, e-mail it and remember who is verifying."""
    code = user.generate_verification_code()
    db.session.commit()
    if send_verification_email(user.email, code):
        session["email_for_verification"] = user.email
        return True
    return False


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_home_for(current_user))

    if request.method == "POST":
        email = clean_text(request.form.get("email"), 150).lower()
        password = request.form.get("password") or ""
        user = User.query.filter(db.func.lower(User.email) == email).first() if email else None

        # Same message for unknown e-mail and wrong password: don't reveal which accounts exist.
        if not user or not user.password or not check_password_hash(user.password, password):
            flash("Incorrect e-mail or password.", category="error")
            return render_template("login.html", email=email), 401

        if not user.is_verified:
            if _start_verification(user):
                flash("Please verify your e-mail first — we've sent you a new code.", category="info")
                return redirect(url_for("auth.verify_email"))
            flash("Your e-mail is not verified and we couldn't send a new code. Please try again later.", category="error")
            return render_template("login.html", email=email), 503

        login_user(user, remember=bool(request.form.get("remember", "on")))
        flash(f"Welcome back, {user.first_name or 'traveller'}!", category="success")
        return redirect(_safe_next_url(request.args.get("next")) or _home_for(user))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("auth.login"))


def _handle_signup(as_guide: bool):
    data, errors = _validate_signup(request.form)
    profile = _guide_profile(request.form, errors) if as_guide else None
    if errors:
        for message in errors:
            flash(message, category="error")
        return None, data

    user = User(
        email=data["email"],
        first_name=data["first_name"],
        password=generate_password_hash(data["password1"]),
        is_guide=as_guide,
        is_verified=False,
    )
    db.session.add(user)
    db.session.flush()
    if as_guide:
        db.session.add(Guide(
            user_id=user.id,
            name=data["first_name"],
            phone=data["phone"],
            experience=profile["experience"],
            languages=", ".join(profile["languages"]),
            specialization=", ".join(profile["specializations"]),
        ))
        db.session.add(GuideDetails(
            user_id=user.id,
            license_number=profile["license"],
            experience_years=profile["experience"],
            languages=", ".join(profile["languages"]),
            specializations=", ".join(profile["specializations"]),
            available_locations=", ".join(profile["locations"])[:500],
        ))
    db.session.commit()

    if _start_verification(user):
        flash("Account created! Check your e-mail for the verification code.", category="success")
        return redirect(url_for("auth.verify_email")), data

    # Roll back the half-created account so the user can retry with the same e-mail.
    if as_guide:
        Guide.query.filter_by(user_id=user.id).delete()
        GuideDetails.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash("We couldn't send the verification e-mail. Please try again in a moment.", category="error")
    return None, data


def _guide_profile(form, errors: list[str]) -> dict:
    """Validate the professional details collected on the guide sign-up form."""
    valid_sites = {site["name"] for site in HERITAGE_SITES}
    profile = {
        "license": clean_text(form.get("license"), 50),
        "experience": parse_int(form.get("experience"), minimum=0, maximum=70),
        "languages": [clean_text(v, 40) for v in form.getlist("languages") if v.strip()][:10],
        "specializations": [clean_text(v, 60) for v in form.getlist("specializations") if v.strip()][:10],
        "locations": [v for v in form.getlist("locations") if v in valid_sites],
    }
    if not is_valid_phone(clean_text(form.get("phone"), 20)):
        errors.append("Please enter a valid phone number.")
    if not profile["license"]:
        errors.append("Please enter your guide licence number.")
    elif GuideDetails.query.filter_by(license_number=profile["license"]).first():
        errors.append("This licence number is already registered.")
    if profile["experience"] is None:
        errors.append("Years of experience must be a number between 0 and 70.")
    if not profile["languages"]:
        errors.append("Please select at least one language.")
    if not profile["locations"]:
        errors.append("Please select at least one site you cover.")
    return profile


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form_data = {}
    if request.method == "POST":
        response, form_data = _handle_signup(as_guide=False)
        if response:
            return response
    return render_template("sign_up.html", form=form_data)


@auth.route("/guide-signup", methods=["GET", "POST"])
def guide_signup():
    form_data = {}
    if request.method == "POST":
        response, form_data = _handle_signup(as_guide=True)
        if response:
            return response
    return render_template("guide_signup.html", form=form_data, sites=HERITAGE_SITES)


@auth.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    email = session.get("email_for_verification")
    if not email:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        user = User.query.filter_by(email=email).first()
        if not user:
            session.pop("email_for_verification", None)
            flash("Account not found. Please sign up again.", category="error")
            return redirect(url_for("auth.sign_up"))

        if user.verify_code(request.form.get("verification_code")):
            db.session.commit()
            session.pop("email_for_verification", None)
            login_user(user, remember=True)
            flash("E-mail verified — welcome to Itihaas!", category="success")
            return redirect(_home_for(user))
        flash("Invalid or expired verification code.", category="error")

    return render_template("verify_email.html", email=email)


@auth.route("/resend-verification")
def resend_verification():
    email = session.get("email_for_verification")
    if not email:
        return redirect(url_for("auth.login"))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Account not found.", category="error")
        return redirect(url_for("auth.login"))
    if _start_verification(user):
        flash("A new verification code is on its way.", category="success")
    else:
        flash("We couldn't send the e-mail. Please try again shortly.", category="error")
    return redirect(url_for("auth.verify_email"))


@auth.route("/update-coins", methods=["POST"])
@login_required
def update_coins():
    """Return the user's current coin balance.

    Kept for backwards compatibility with older front-end code. Coins are now
    awarded and spent exclusively on the server as part of
    ``/api/process-booking-payment``; client-supplied ``reward_coins`` are
    ignored so balances cannot be inflated from the browser.
    """
    return jsonify({"success": True, "new_balance": current_user.coin_balance})
