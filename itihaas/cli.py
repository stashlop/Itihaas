"""Custom ``flask`` CLI commands.

Usage (from the repository root)::

    flask --app itihaas seed
    flask --app itihaas create-admin you@example.com
    flask --app itihaas whatsapp-dispatch
"""
from __future__ import annotations

import getpass
import time

import click
from flask import Flask, current_app
from werkzeug.security import generate_password_hash

from .extensions import db


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command():
        """Load demo merchandise into the shop."""
        from .seed import seed_merchandise

        added = seed_merchandise()
        click.echo(f"Seeded {added} product(s).")

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.option("--name", default="Admin", show_default=True)
    def create_admin_command(email: str, name: str):
        """Create (or reset) a verified account for EMAIL.

        The address must also be listed in ADMIN_EMAILS to get admin access.
        """
        from .models import User

        email = email.strip().lower()
        password = getpass.getpass("Password (min 8 chars): ")
        if len(password) < 8:
            raise click.ClickException("Password must be at least 8 characters.")
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user is None:
            user = User(email=email, first_name=name)
            db.session.add(user)
        user.password = generate_password_hash(password)
        user.is_verified = True
        db.session.commit()
        if email not in current_app.config["ADMIN_EMAILS"]:
            click.echo(f"Note: add {email} to ADMIN_EMAILS in your .env to grant admin access.")
        click.echo(f"Account ready: {email}")

    @app.cli.command("whatsapp-dispatch")
    @click.option("--limit", default=5, show_default=True, help="Bookings to process per run.")
    @click.option("--loop", is_flag=True, help="Keep running, checking every 2 minutes.")
    def whatsapp_dispatch_command(limit: int, loop: bool):
        """Send pending WhatsApp booking confirmations (requires pywhatkit)."""
        from .models import Booking
        from .whatsapp import send_booking_confirmation

        while True:
            pending = (
                Booking.query.filter(Booking.status.in_(["Confirmed", "Successful"]), Booking.whatsapp_sent.is_(False))
                .limit(limit)
                .all()
            )
            for booking in pending:
                ok, message = send_booking_confirmation(booking.phone, {
                    "id": booking.id, "name": booking.name, "monument_name": booking.monument_name,
                    "visit_date": booking.visit_date, "visitors": booking.visitors,
                    "total_amount": booking.total_amount,
                })
                if ok:
                    booking.whatsapp_sent = True
                    db.session.commit()
                click.echo(f"Booking {booking.id}: {'sent' if ok else 'failed — ' + message}")
            if not loop:
                break
            time.sleep(120)
