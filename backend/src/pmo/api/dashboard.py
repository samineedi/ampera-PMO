from flask import Blueprint, jsonify, request

from pmo.api import common
from pmo.domain.dashboard import dashboard_view, project_names

bp = Blueprint("dashboard", __name__)
MODULES = {"dashboard", "digest", "planning", "closure"}


@bp.get("/api/projects")
def projects():
    return jsonify(projects=project_names(common.board()["items"]))


@bp.get("/api/dashboard")
def dashboard():
    return jsonify(dashboard_view(common.board()["items"], request.args.get("project")))


@bp.post("/api/refresh/<module>")
def refresh(module):
    if module not in MODULES:
        return jsonify(error="Unknown module"), 404
    try:
        b = common.board(refresh=True)
    except Exception as e:
        common.log.exception("Refresh failed")
        return jsonify(error=f"Could not refresh from Trello: {e}"), 502
    return jsonify(status="ok", fetched_at=common.fmt(b["fetched_at"]), items=len(b["items"]))
