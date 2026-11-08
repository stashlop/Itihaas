"""Server-side proxies for third-party APIs.

Keeping these calls on the server means API keys never reach the browser,
responses can be normalised and cached, and the UI degrades gracefully when an
integration is not configured.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import requests
from flask import Blueprint, current_app, jsonify, request

from .utils import json_error, parse_float

api = Blueprint("api", __name__, url_prefix="/api")
log = logging.getLogger(__name__)

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_NEWS_QUERY = '(heritage OR monument OR "Taj Mahal" OR "Red Fort" OR tourism) AND India'
CACHE_TTL_SECONDS = 600

_cache: dict[str, tuple[float, Any]] = {}


def _cached(key: str):
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < CACHE_TTL_SECONDS:
        return hit[1]
    return None


def _store(key: str, value: Any) -> Any:
    if len(_cache) > 256:  # keep memory bounded
        _cache.clear()
    _cache[key] = (time.monotonic(), value)
    return value


@api.route("/news")
def news():
    """Search heritage & tourism news (NewsAPI.org format)."""
    api_key = current_app.config.get("NEWS_API_KEY")
    if not api_key:
        return json_error("News is not configured on this server.", 503, articles=[], configured=False)

    query = (request.args.get("q") or "").strip()[:200] or DEFAULT_NEWS_QUERY
    cache_key = f"news:{query.lower()}"
    if (cached := _cached(cache_key)) is not None:
        return jsonify(cached)

    try:
        response = requests.get(
            NEWS_ENDPOINT,
            params={"q": query, "language": "en", "sortBy": "publishedAt", "pageSize": 24},
            headers={"X-Api-Key": api_key},
            timeout=current_app.config["HTTP_TIMEOUT_SECONDS"],
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        log.exception("News API request failed")
        return json_error("News service is temporarily unavailable.", 502, articles=[])

    articles = [
        {
            "title": item.get("title") or "Untitled",
            "description": item.get("description") or "",
            "url": item.get("url"),
            "urlToImage": item.get("urlToImage"),
            "publishedAt": item.get("publishedAt") or "",
            "source": {"name": (item.get("source") or {}).get("name") or "Unknown"},
        }
        for item in payload.get("articles", [])
        if item.get("url", "").startswith(("http://", "https://")) and item.get("title") != "[Removed]"
    ]
    return jsonify(_store(cache_key, {"status": "ok", "articles": articles}))


@api.route("/weather")
def weather():
    """Current weather for a coordinate (OpenWeather)."""
    api_key = current_app.config.get("OPENWEATHER_API_KEY")
    if not api_key:
        return json_error("Weather is not configured on this server.", 503, configured=False)

    lat = parse_float(request.args.get("lat"), minimum=-90, maximum=90)
    lng = parse_float(request.args.get("lng"), minimum=-180, maximum=180)
    if lat is None or lng is None:
        return json_error("Valid 'lat' and 'lng' query parameters are required.")

    cache_key = f"weather:{lat:.2f}:{lng:.2f}"
    if (cached := _cached(cache_key)) is not None:
        return jsonify(cached)

    try:
        response = requests.get(
            WEATHER_ENDPOINT,
            params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"},
            timeout=current_app.config["HTTP_TIMEOUT_SECONDS"],
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        log.exception("Weather API request failed")
        return json_error("Weather service is temporarily unavailable.", 502)

    # Return the same shape OpenWeather does for the fields the map uses.
    return jsonify(_store(cache_key, {
        "main": payload.get("main", {}),
        "weather": payload.get("weather", []),
        "wind": payload.get("wind", {}),
        "name": payload.get("name"),
    }))
