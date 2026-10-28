from flask import Blueprint, jsonify

from pmo.agents.drafter import _get_llm
from pmo.agents.planner import create_trello_cards, parse_team
from pmo.api import common

bp = Blueprint("planning", __name__)


@bp.post("/api/plan")
def plan():
    d = common.body()
    if not d.get("brief", "").strip():
        return jsonify(error="Please enter a project brief"), 400
    team = parse_team(d.get("team_text", ""))
    if not team:
        return jsonify(error="Please enter at least one team member"), 400
    res = common.graph().invoke({"mode": "plan", "brief": d["brief"], "team": team})
    return jsonify(plan=res["plan"], llm_used=_get_llm() is not None)


@bp.post("/api/plan/create")
def plan_create():
    d = common.body()
    plan = d.get("plan") or []
    if not plan:
        return jsonify(error="The plan is empty"), 400
    dry = bool(d.get("dry_run", True))
    msg = create_trello_cards(plan, None, dry_run=dry, project=(d.get("project") or "").strip() or None)
    if not dry:
        try:
            common.board(refresh=True)
        except Exception:
            common.log.exception("Refresh after card creation failed")
    return jsonify(message=msg)
