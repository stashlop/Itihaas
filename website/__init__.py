"""Shim package to preserve legacy imports expecting a `website` package.
This file re-exports modules from the project root where appropriate.
"""
from importlib import import_module

def _import(name):
    try:
        return import_module(name)
    except Exception:
        return None

translations = _import('translations')
chatbot = _import('chatbot')

# Provide expected attributes if modules exist
if translations:
    try:
        translations = translations
    except Exception:
        translations = None

if chatbot:
    try:
        chatbot_bp = getattr(chatbot, 'chatbot_bp', None)
    except Exception:
        chatbot_bp = None
