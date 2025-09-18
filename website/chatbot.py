try:
    from chatbot import chatbot_bp as chatbot_bp
except Exception:
    # Minimal fallback blueprint to avoid import errors
    from flask import Blueprint
    chatbot_bp = Blueprint('chatbot', __name__)
