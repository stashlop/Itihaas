"""WSGI entry point for production servers (``gunicorn wsgi:app``)."""
from itihaas import create_app

app = create_app()
