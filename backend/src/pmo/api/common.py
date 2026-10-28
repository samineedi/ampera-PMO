"""Helpers shared by the API blueprints."""
import logging
from datetime import datetime

from flask import request

from pmo.services import cache

log = logging.getLogger("pmo")
_graph = None


def graph():
    """The LangGraph workflow, built on first use (importing it pulls in the LLM libraries)."""
    global _graph
    if _graph is None:
        from pmo.agents.graph import build_graph
        _graph = build_graph()
    return _graph


def board(refresh=False):
    return cache.get_board(refresh=refresh)


def fmt(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %H:%M UTC")
    except (TypeError, ValueError):
        return "never"


def body():
    return request.get_json(silent=True) or {}
