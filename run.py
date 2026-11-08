"""Local development entry point: ``python run.py``.

For production use a WSGI server, e.g. ``gunicorn wsgi:app``.
"""
import os

from itihaas import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_RUN_PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
