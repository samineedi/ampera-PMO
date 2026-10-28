from datetime import datetime, timedelta, timezone

from pmo.domain.classify import classify
from pmo.domain.kpi import compute_kpis
from pmo.domain.risk import build_risk_radar


def titles(rows):
    return {r["title"] for r in rows}


def test_classify_sorts_items_into_sections(items):
    s = classify(items)
    assert titles(s["completed"]) == {"Done one"}
    assert titles(s["in_progress"]) == {"Working", "Late"}
    assert titles(s["blocked"]) == {"Stuck"}
    assert titles(s["overdue"]) == {"Late"}


def test_classify_ignores_old_completions(make_card):
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    assert classify([make_card("Old", status="done", completed_at=old)])["completed"] == []


def test_kpis_health_thresholds(items):
    k = compute_kpis(items, classify(items))
    assert (k["completed_this_week"], k["blocked"], k["overdue"], k["health"]) == (1, 1, 1, "AMBER")


def test_kpis_green_when_nothing_wrong(make_card):
    its = [make_card("Fine", status="in_progress")]
    assert compute_kpis(its, classify(its))["health"] == "GREEN"


def test_kpis_red_with_three_blocked(make_card):
    its = [make_card(f"B{n}", status="blocked") for n in range(3)]
    assert compute_kpis(its, classify(its))["health"] == "RED"


def test_risk_radar_flags_blocked_and_overdue(items):
    rows = {r["title"]: r for r in build_risk_radar(items)}
    assert "Blocked: waiting on vendor" in rows["Stuck"]["reasons"]
    assert rows["Late"]["reasons"] == ["Overdue 5d"] and rows["Late"]["severity"] == "High"
    assert "Working" not in rows and "Done one" not in rows
