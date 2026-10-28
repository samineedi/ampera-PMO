from flask import Blueprint, jsonify

from pmo.api import common
from pmo.domain.dashboard import filter_project
from pmo.integrations.sender import send_report
from pmo.services.closure import archive_board, assess

bp = Blueprint("closure", __name__)


@bp.post("/api/closure/run")
def closure_run():
    d = common.body()
    project = d.get("project")
    res = common.graph().invoke({"mode": "closure", "items": filter_project(common.board()["items"], project),
                                 "project_name": d.get("project_name") or project or "Project"})
    a = res["closure"]
    return jsonify(kpis=a["kpis"], ready=a["ready_to_close"], draft=res["closure_draft"],
                   outstanding=[i["title"] for i in a["sections"]["outstanding"]])


@bp.post("/api/closure/send")
def closure_send():
    d = common.body()
    text = d.get("text", "").strip()
    if not text:
        return jsonify(error="Report is empty"), 400
    return jsonify(message=send_report(text, subject=f"Closure Report - {d.get('project_name') or 'Project'}"))


@bp.post("/api/closure/archive")
def closure_archive():
    d = common.body()
    if not assess(common.board()["items"])["ready_to_close"]:       # checked on the server, not just in the UI
        return jsonify(error="Open items remain - the board cannot be archived yet."), 400
    if d.get("dry_run", True):
        return jsonify(message="Dry run - nothing was archived.")
    return jsonify(message=archive_board(None, confirm=bool(d.get("confirm"))))
