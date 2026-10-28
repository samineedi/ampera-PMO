"""Weekly report: KPIs, risks, editable draft, sending, reminders."""
import re
from datetime import datetime

from flask import Blueprint, jsonify, request

from pmo import config
from pmo.agents.drafter import _get_llm
from pmo.api import common
from pmo.domain.dashboard import filter_project
from pmo.integrations.sender import send_report
from pmo.services import cache
from pmo.services.notifier import build_notifications, send_notifications

bp = Blueprint("digest", __name__)


def _draft_key(project):
    return "digest_draft_" + (re.sub(r"[^a-z0-9]+", "_", project.lower()).strip("_") if project else "all")


@bp.get("/api/digest")
def digest():
    project = request.args.get("project")
    items = filter_project(common.board()["items"], project)
    res = common.graph().invoke({"mode": "weekly", "items": items, "days": config.LOOKBACK_DAYS, "use_llm": False})
    saved = cache.load(_draft_key(project))
    return jsonify(kpis=res["kpis"], risk=res["risk"], sections=res["sections"], notifications=res["notifications"],
                   days=config.LOOKBACK_DAYS, draft=saved["draft"] if saved else res["draft"],
                   draft_time=common.fmt(saved["generated_at"]) if saved else None, llm_available=_get_llm() is not None)


@bp.post("/api/digest/draft")
def digest_draft():
    project = common.body().get("project")
    items = filter_project(common.board()["items"], project)
    res = common.graph().invoke({"mode": "weekly", "items": items, "days": config.LOOKBACK_DAYS, "use_llm": True})
    cache.save(_draft_key(project), {"draft": res["draft"], "generated_at": datetime.utcnow().isoformat() + "+00:00"})
    return jsonify(draft=res["draft"], llm_used=_get_llm() is not None)


@bp.post("/api/digest/send")
def digest_send():
    text = common.body().get("text", "").strip()
    if not text:
        return jsonify(error="Draft is empty"), 400
    return jsonify(message=send_report(text, subject="Weekly Status Report"))


@bp.post("/api/notifications/send")
def notifications_send():
    d = common.body()
    dry = bool(d.get("dry_run", True))
    msgs = build_notifications(filter_project(common.board()["items"], d.get("project")))
    if not msgs:
        return jsonify(message="Nothing to send.")
    return jsonify(message=send_notifications(msgs, dry_run=dry))
