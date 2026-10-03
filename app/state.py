"""Explicit, testable session transitions; no analytical calculations live here."""

from copy import deepcopy

PAGES = ["Home", "Signals", "Investigate", "Scenario Lab", "Ask PULSE", "Briefs"]
DOMAINS = {
    "operating_profit": "Profitability",
    "gross_profit": "Profitability",
    "revenue": "Commercial",
    "labour_pct": "Operations",
    "stockout_rate": "Inventory",
    "refund_rate": "Customer",
    "satisfaction": "Customer",
}
SCENARIO_DEFAULTS = {
    "price_change": 0,
    "transaction_change": 0,
    "basket_change": 0,
    "hours_change": 0,
    "wage_change": 0,
    "retention_change": 0,
    "promotion_uptake_change": 0,
    "replace_discount": False,
    "replace_margin": False,
}


def signal_id(row):
    return f"{int(row['location_id'])}:{row['kpi']}:{row['timestamp']}"


def context(start, end, location=None, entity="Company", state="All", kpi="operating_profit"):
    if start > end:
        raise ValueError("Context start must not follow end")
    return dict(start=start, end=end, location=location, entity=entity, state=state, kpi=kpi)


def initialise(session, start, end):
    session.setdefault("nav", "Home")
    if session["nav"] not in PAGES:
        session["nav"] = "Home"
    session.setdefault("context", context(start, end))
    for key, default in {
        "signal_status": {},
        "brief_items": [],
        "scenarios": [],
        "decisions": [],
        "demo_step": None,
        "selected_signal": None,
        "comparison": session.get("comparison_mode", "Previous period"),
    }.items():
        session.setdefault(key, deepcopy(default))


def reset_assumptions(session):
    session.pop("scenario_inputs", None)
    for key, value in SCENARIO_DEFAULTS.items():
        session[f"scenario_{key}"] = value
    for key in ["scenario_discount_rate", "scenario_product_margin", "scenario_current"]:
        session.pop(key, None)


def set_context(session, new_context, signal=None):
    if session.get("context") != new_context:
        reset_assumptions(session)
        session.pop("ask_result", None)
        session.pop("ask_question", None)
        session.pop("ask_text", None)
    session["context"] = deepcopy(new_context)
    session["selected_signal"] = deepcopy(signal)


def update_scenario_inputs(session, **values):
    """Retain authoritative controls independently of disposable widget state."""
    session.setdefault("scenario_inputs", {}).update(values)
    for field, value in values.items():
        session["scenario_" + field] = value


def select_signal(session, row, locations):
    row = dict(row)
    row["location_id"] = int(row["location_id"])
    info = locations.loc[locations.location_id == row["location_id"]].iloc[0]
    set_context(
        session,
        context(
            row["period_start"],
            row["timestamp"],
            row["location_id"],
            row["entity"],
            info.state,
            row["kpi"],
        ),
        row,
    )
    session["pulse_selector"] = signal_id(row)


def navigate(session, page):
    if page not in PAGES:
        raise ValueError("Unknown product destination")
    session["nav"] = page


def reset_context(session, start, end):
    set_context(session, context(start, end))
    session["demo_step"] = None
    session["comparison"] = "Previous period"
    session["comparison_mode"] = "Previous period"
    session.pop("pulse_selector", None)
    session.pop("pulse_event_signature", None)
    session["feedback"] = "Context reset to the company’s latest complete week."


def filter_signals(
    frame,
    statuses,
    severity="All",
    domain="All",
    entity="All",
    kpi="All",
    status="All",
    period="All",
):
    out = frame.copy()
    out["domain"] = out.kpi.map(DOMAINS)
    out["status"] = [statuses.get(signal_id(row), "Open") for row in out.to_dict("records")]
    for column, value in [
        ("severity", severity),
        ("domain", domain),
        ("entity", entity),
        ("kpi", kpi),
        ("status", status),
        ("timestamp", period),
    ]:
        if value != "All":
            out = out[out[column] == value]
    return out


def acknowledge(session, row):
    session["signal_status"][signal_id(row)] = "Acknowledged"
    session["feedback"] = f"{row['entity']} signal acknowledged for this session."


def add_to_brief(session, row):
    identifier = signal_id(row)
    if not any(item["id"] == identifier for item in session["brief_items"]):
        session["brief_items"].append({"id": identifier, "signal": deepcopy(dict(row))})
    session["feedback"] = f"{row['entity']} evidence is in your brief."


def move_brief(session, identifier, offset):
    items = session["brief_items"]
    indices = [i for i, item in enumerate(items) if item["id"] == identifier]
    if not indices:
        return
    index = indices[0]
    target = index + offset
    if 0 <= target < len(items):
        items[index], items[target] = items[target], items[index]


def remove_brief(session, identifier):
    session["brief_items"] = [item for item in session["brief_items"] if item["id"] != identifier]


def reset_filters(session):
    session["signal_filters"] = {}
    for name in ["severity", "domain", "entity", "kpi", "status", "period"]:
        session[f"filter_{name}"] = "All"


def context_question(question, ctx):
    """Build an explicit engine scope; supported periods are latest week/month."""
    if not question.strip() or len(question) > 500:
        return question
    scoped = question.strip()
    if ctx["location"] is not None and ctx["entity"].lower() not in scoped.lower():
        scoped += f" in {ctx['entity']}"
    if ctx["start"].endswith("-01") and (int(ctx["end"][-2:]) - 1) >= 27:
        scoped += " last month" if "month" not in scoped.lower() else ""
    return scoped
