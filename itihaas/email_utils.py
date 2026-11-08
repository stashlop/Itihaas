"""Transactional e-mail helpers."""
from __future__ import annotations

import logging

from flask import current_app, render_template
from flask_mail import Message

from .extensions import mail

logger = logging.getLogger(__name__)


def email_configured() -> bool:
    config = current_app.config
    return bool(config.get("MAIL_USERNAME") and config.get("MAIL_PASSWORD"))


def send_verification_email(user_email: str, verification_code: str) -> bool:
    """Send the sign-up verification code.

    When SMTP credentials are missing and the app runs in debug/testing mode,
    the code is written to the server log instead, so the sign-up flow can be
    exercised locally without a mail account.
    """
    if not email_configured():
        if (current_app.debug or current_app.testing) and current_app.config.get("MAIL_DEV_LOG_CODES"):
            logger.warning("E-mail not configured — verification code for %s is %s", user_email, verification_code)
            return True
        logger.error("E-mail is not configured. Set EMAIL_USER and EMAIL_PASSWORD.")
        return False

    msg = Message(
        "Verify your Itihaas account",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user_email],
    )
    msg.body = (
        f"Welcome to Itihaas!\n\nYour verification code is {verification_code}.\n"
        "It expires in 10 minutes.\n\nIf you did not sign up, you can ignore this e-mail."
    )
    msg.html = render_template("emails/verification.html", code=verification_code)
    try:
        mail.send(msg)
    except Exception:  # SMTP errors come in many shapes
        logger.exception("Failed to send verification e-mail to %s", user_email)
        return False
    logger.info("Sent verification e-mail to %s", user_email)
    return True
