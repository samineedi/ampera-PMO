"""Application factory.

    python -m pmo  ->  http://localhost:5000   (needs `npm run build` in frontend/ once)
    cd frontend && npm run dev  ->  http://localhost:5173 with /api proxied to Flask
    gunicorn "pmo.main:create_app()"            (production)

Pages (React routes): /dashboard   /weekly-report   /planning   /closure
Pattern per module: GET /api/<module> (JSON), POST /api/refresh/<module>.
Trello is the only data source. The board is fetched once into a JSON cache (refreshed every 30 min in the background) and every page
reads it from there, so opening a page never calls Trello.
"""
import logging
import os

from flask import Flask

from pmo import config
from pmo.api import BLUEPRINTS, system
from pmo.api.auth import check_config, init_auth
from pmo.services import cache

log = logging.getLogger("pmo")
REQUIRED = ("TRELLO_API_KEY", "TRELLO_TOKEN", "TRELLO_BOARD_ID")


def create_app():
    # Fail fast: never start half-configured.
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing required settings in .env: {', '.join(missing)}")
    check_config()

    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
    if os.getenv("TRUST_PROXY", "false").lower() == "true":      # behind Azure / a reverse proxy: use the real client IP and scheme
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    init_auth(app)
    system.register_hooks(app)
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)
    return app


def start_background_refresh():
    """Refresh the board cache every CACHE_REFRESH_MINUTES (set DISABLE_BG_REFRESH=true to turn off)."""
    if os.getenv("DISABLE_BG_REFRESH", "false").lower() == "true":
        return
    from apscheduler.schedulers.background import BackgroundScheduler

    def job():
        try:
            cache.refresh_board()
            log.info("Cache refreshed: board")
        except Exception:
            log.exception("Background refresh failed")

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(job, "interval", minutes=config.CACHE_REFRESH_MINUTES, id="board-refresh",
                  max_instances=1, coalesce=True)
    sched.start()
