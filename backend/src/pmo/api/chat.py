from flask import Blueprint, jsonify, request

from pmo.agents.chat_agent import ChatUnavailable, ask
from pmo.api import common

bp = Blueprint("chat", __name__)


def _valid_history(h):
    return isinstance(h, list) and all(isinstance(m, dict) and m.get("role") in ("user", "assistant")
                                       and isinstance(m.get("content"), str) for m in h)


@bp.post("/api/chat")
def chat():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="Expected a JSON body"), 400
    message, history, project = body.get("message"), body.get("history", []), body.get("project", "")
    if not isinstance(message, str) or not message.strip() or len(message) > 1000:
        return jsonify(error="message must be 1-1000 characters"), 400
    if not _valid_history(history):
        return jsonify(error="history must be a list of {role: user|assistant, content: string}"), 400
    if not isinstance(project, str):
        return jsonify(error="project must be a string"), 400
    try:
        return jsonify(ask(common.board()["items"], message.strip(), history, project))
    except ChatUnavailable as e:
        return jsonify(error=str(e)), 503
    except Exception:
        common.log.exception("Chat failed")
        return jsonify(error="The assistant had a problem answering. Please try again."), 502
