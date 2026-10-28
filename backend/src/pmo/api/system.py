"""Health, cache status, the React shell and the cross-cutting HTTP hooks (headers, error handling)."""
import os

import requests
from flask import Blueprint, jsonify, request, send_from_directory

from pmo import config
from pmo.api import common
from pmo.integrations.trello import BASE
from pmo.services import cache

bp = Blueprint("system", __name__)
DIST = config.ROOT / "frontend" / "dist"


@bp.get("/ping")
def ping():
    return jsonify(status="ok")


@bp.get("/api/meta")
def meta():
    b = cache.load("board")
    return jsonify(fetched_at=common.fmt(b["fetched_at"]) if b else "not loaded")


@bp.get("/api/trello-health")
def trello_health():
    try:
        r = requests.get(f"{BASE}/members/me", params={"key": os.getenv("TRELLO_API_KEY"),
                         "token": os.getenv("TRELLO_TOKEN"), "fields": "username"}, timeout=15)
        return jsonify(status="ok" if r.ok else "error", http=r.status_code), (200 if r.ok else 502)
    except requests.RequestException as e:
        return jsonify(status="error", detail=str(e)), 502


@bp.get("/", defaults={"path": ""})
@bp.get("/<path:path>")
def serve_spa(path):
    if path and (DIST / path).is_file():
        return send_from_directory(DIST, path)
    if path.startswith(("api/", "assets/")):
        return jsonify(error="Not found"), 404
    if not (DIST / "index.html").is_file():
        return ("Frontend not built. Run: cd frontend && npm install && npm run build", 503)
    return send_from_directory(DIST, "index.html")


def register_hooks(app):
    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["X-XSS-Protection"] = "1; mode=block"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return resp

    @app.errorhandler(Exception)
    def on_error(e):
        code = getattr(e, "code", 500) if hasattr(e, "code") and isinstance(getattr(e, "code"), int) else 500
        if code >= 500:
            common.log.exception("Unhandled error")
        if request.path.startswith("/api/"):
            return jsonify(error=str(e)), code
        if code == 404 and request.method == "GET":                  # client-side routes fall through to the SPA
            return serve_spa(request.path.lstrip("/"))
        return jsonify(error=str(e)), code
