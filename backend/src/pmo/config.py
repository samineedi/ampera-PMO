"""Edit these to match how your Trello board is organised (list/label names are lowercase)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")          # repo-root .env, whatever the working directory

# --- Status mapping (Trello list names / labels) ---
DONE_LISTS = {"done", "completed", "closed", "released"}
IN_PROGRESS_LISTS = {"doing", "in progress", "in review", "review", "testing", "qa"}
BLOCKED_LISTS = {"blocked", "on hold"}
BLOCKED_LABELS = {"blocked", "impediment"}

# --- Time windows / thresholds ---
LOOKBACK_DAYS = 7
UPCOMING_DAYS = 7
DUE_SOON_DAYS = 2
STALE_DAYS = 5               # no activity this long => stuck
ESCALATE_OVERDUE_DAYS = 3

# --- Planning ---
TODO_LISTS = ["to do", "todo", "backlog"]   # new planned cards are created in the first matching list

# --- Label conventions (works on a free Trello plan) ---
# A card is tagged with labels such as:  "Project: Project 1"  "Release: v1.4"  "Team: Backend"  "Phase: QA"
#                                        "Sprint: 12"  "Type: Epic"  "Sev: Critical"
LABEL_PREFIXES = {
    "project": "project:", "release": "release:", "team": "team:", "phase": "phase:",
    "sprint": "sprint:", "type": "type:", "severity": "sev:",
}

# --- Pipeline (Backlog > Development > Testing > Done) ---
STAGES = ["Backlog", "Development", "Testing", "Done"]
STAGE_BY_LIST = {
    "backlog": "Backlog", "to do": "Backlog", "todo": "Backlog",
    "doing": "Development", "in progress": "Development", "blocked": "Development", "on hold": "Development",
    "in review": "Testing", "review": "Testing", "testing": "Testing", "qa": "Testing",
    "done": "Done", "completed": "Done", "closed": "Done", "released": "Done",
}

# --- Data / cache ---
EPICS_ONLY = os.getenv("EPICS_ONLY", "false").lower() == "true"   # true: dashboards count only "Type: Epic" cards
ROOT = Path(__file__).resolve().parents[3]                          # repository root (backend/src/pmo/config.py -> ../../..)
DATA_DIR = ROOT / "data"                                           # runtime output, git-ignored


def _dir(env, default):
    """Folder from an env override (relative paths resolve against the repo root) or the default under data/."""
    return ROOT / os.environ[env] if os.getenv(env) else default


def cache_dir():
    return _dir("CACHE_DIR", DATA_DIR / "cache")


def reports_dir():
    return _dir("REPORTS_DIR", DATA_DIR / "reports")



CACHE_REFRESH_MINUTES = int(os.getenv("CACHE_REFRESH_MINUTES", "30"))
