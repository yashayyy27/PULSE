import math
import numpy as np
import pandas as pd
import pytest
from pulse.alerts.engine import detect, exposure_summary, robust_warning
from pulse.analytics.core import bridge, contributions, daily, investigate, latest_week
from pulse.analytics.health import health
from pulse.analytics.impact import stockout_opportunity
from pulse.data.generator import frames
from pulse.data.validation import validate
from pulse.forecasting.engine import errors, forecast, predict
from pulse.metrics.registry import REGISTRY, calculate
from pulse.query.ask import EXAMPLES, answer
from pulse.runtime import connect, query, read_sql
from pulse.scenarios.engine import Assumptions, simulate


def test_governed_ledger():
    b = dict(
        list_sales=1000,
        discounts=100,
        refunds=20,
        cogs=300,
        labour_cost=200,
        channel_fees=30,
        overhead=50,
        campaign_spend=10,
        transactions=40,
        labour_hours=10,
        stockouts=2,
        inventory_checks=20,
        refunded_transactions=1,
        rating_sum=21,
        responses=5,
    )
    x = calculate(b)
    assert x["revenue"] == 880 and x["gross_profit"] == 580 and x["operating_profit"] == 290
    assert x["aov"] == 22 and x["labour_pct"] == pytest.approx(200 / 880)
    assert x["refund_rate"] == 0.025 and x["stockout_rate"] == 0.1 and x["satisfaction"] == 4.2
    assert math.isnan(calculate({**b, "transactions": 0})["aov"])
    assert len(REGISTRY) == 19


def test_sql_reconciliation(demo):
    frame = query("SELECT * FROM mart_daily", path=demo)
    expected = query(
        "SELECT SUM(list_sales-discount-refund) revenue,SUM(cogs) cogs FROM fact_sales", path=demo
    ).iloc[0]
    assert frame.revenue.sum() == pytest.approx(expected.revenue)
    assert frame.cogs.sum() == pytest.approx(expected.cogs)
    payroll = query("SELECT SUM(labour_cost) value FROM fact_labour", path=demo).iloc[0, 0]
    assert frame.labour_cost.sum() == pytest.approx(payroll) and len(frame) == 6 * 210
    with connect(demo) as con:
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
        with pytest.raises(Exception):
            con.execute("DELETE FROM dim_location")


def test_validation_detects_corruption():
    t = frames(small=True)
    assert validate(t).failures.sum() == 0
    t["fact_sales"].loc[0, "location_id"] = 999
    t["fact_sales"].loc[1, "discount"] = 9999
    t["fact_sales"].loc[2, "daypart"] = "Night"
    t["fact_sales"].loc[3, "sale_id"] = t["fact_sales"].loc[4, "sale_id"]
    t["fact_labour"].loc[0, "hours"] = -1
    t["fact_inventory"] = t["fact_inventory"].iloc[12:]
    q = validate(t).set_index("rule")
    for name in [
        "fact_sales: location_id FK",
        "sales: ledger bounds",
        "sales: daypart",
        "fact_sales: unique key",
        "labour: hours",
        "inventory: SKU coverage",
    ]:
        assert q.loc[name, "status"] == "FAIL"


def test_seed_reproducibility():
    a, b = frames(42, True), frames(42, True)
    pd.testing.assert_frame_equal(a["fact_sales"], b["fact_sales"])
    assert not a["fact_sales"].equals(frames(43, True)["fact_sales"])


def test_bridge_and_dimensions(demo):
    start, end = latest_week(demo)
    inv = investigate(start, end, path=demo)
    assert inv["bridge"].impact.sum() == pytest.approx(
        inv["after"]["operating_profit"] - inv["before"]["operating_profit"]
    )
    for dimension in [
        "State",
        "Region",
        "Location",
        "Category",
        "Product",
        "Channel",
        "Daypart",
        "Weekday",
        "Customer segment",
        "Promotion",
    ]:
        frame = contributions(start, end, dimension, path=demo)
        assert frame.contribution.sum() == pytest.approx(
            inv["after"]["revenue"] - inv["before"]["revenue"]
        )
    with pytest.raises(ValueError):
        contributions(start, end, "DROP TABLE", path=demo)


def test_bridge_known_inputs(baseline):
    old = {**baseline, "list_sales": 100, "transactions": 10}
    new = {**old, "list_sales": 144, "transactions": 12, "labour_cost": old["labour_cost"] + 7}
    rows = bridge(old, new).set_index("contributor").impact
    assert rows["Order volume"] == 20 and rows["Basket / price / product mix"] == 24
    assert rows["Labour cost"] == -7


def test_anomaly_edges():
    assert robust_warning(100, [100] * 8, -1) is None
    assert robust_warning(70, [100] * 8, -1)["baseline"] == 100
    assert robust_warning(130, [100] * 8, -1) is None
    assert robust_warning(70, [100] * 7, -1) is None
    assert robust_warning(-150, [-100] * 8, -1) is not None
    assert robust_warning(float("nan"), [100] * 8, -1) is None


def test_alert_and_exposure(demo):
    alerts = detect(demo)
    if len(alerts):
        assert alerts.actual.notna().all()
        assert alerts.timestamp.eq(latest_week(demo)[1]).all()
    fake = pd.DataFrame(
        {
            "kpi": ["operating_profit", "revenue", "operating_profit"],
            "location_id": [1, 1, 1],
            "estimated_profit_exposure": [200, 500, 200],
        }
    )
    assert exposure_summary(fake) == 200


def test_scenarios_identity_and_sensitivity(baseline):
    same = simulate(baseline)
    for key in ["revenue", "gross_profit", "operating_profit", "labour_cost", "cogs"]:
        assert same[key] == pytest.approx(baseline[key])
    raised = simulate(baseline, Assumptions(price_change=0.1))
    assert raised["revenue"] == pytest.approx(baseline["revenue"] * 1.1)
    assert raised["cogs"] == baseline["cogs"]
    cut = simulate(baseline, Assumptions(hours_change=-0.1))
    assert cut["operating_profit"] - baseline["operating_profit"] == pytest.approx(
        baseline["labour_cost"] * 0.1
    )
    for assumption in [
        Assumptions(price_change=-1),
        Assumptions(discount_rate=2),
        Assumptions(product_margin=float("nan")),
    ]:
        with pytest.raises(ValueError):
            simulate(baseline, assumption)


def test_forecast_chronology(demo):
    series = np.tile([10, 20, 30, 40, 50, 60, 70], 30)
    assert np.allclose(predict(series, "Seasonal naive"), series[-28:])
    assert errors([0, 0], [1, 1])["MAPE"] is None
    result = forecast(daily(demo))
    assert len(result["future"]) == 112
    assert result["future"].lower.le(result["future"].forecast).all()
    changed = daily(demo)
    changed.loc[changed.index[-28:], "revenue"] *= 3
    b = forecast(changed)
    assert result["metrics"].selected_model.tolist() == b["metrics"].selected_model.tolist()
    assert np.allclose(
        result["future"].upper - result["future"].forecast, b["future"].upper - b["future"].forecast
    )
    with pytest.raises(ValueError):
        forecast(changed.iloc[:40])


def test_health_and_opportunity(demo, baseline):
    h = health(baseline)
    assert 0 <= h["overall"] <= 100 and sum(h["normalised_weights"].values()) == pytest.approx(1)
    with pytest.raises(ValueError):
        health(baseline, {"Financial": 0, "Customer": 0, "Operations": 0, "Inventory": 0})
    a = stockout_opportunity("2025-11-01", "2025-12-28", path=demo, substitution=0)
    b = stockout_opportunity("2025-11-01", "2025-12-28", path=demo, substitution=1)
    assert b.estimated_revenue_opportunity.sum() == 0 and a.estimated_revenue_opportunity.sum() >= 0


@pytest.mark.parametrize("question", EXAMPLES)
def test_ask_evidence(demo, question):
    result = answer(question, demo)
    assert result["supported"] and result["evidence"] is not None and result["limitations"]


def test_unknown_and_sql_injection(demo):
    assert not answer("Predict the stock market", demo)["supported"]
    assert not answer("DROP TABLE fact_sales", demo)["supported"]
    assert answer("profit in Newcastle last month", demo)["scope"] == "2"


def test_cohorts_retention_and_promotions(demo):
    r = query("SELECT * FROM mart_retention", path=demo)
    assert pd.isna(r.iloc[-1].retention) and r.retention.dropna().between(0, 1).all()
    cohort = query("SELECT * FROM mart_cohorts", path=demo)
    assert cohort[cohort.cohort == cohort.month].retention.eq(1).all()
    assert len(query("SELECT * FROM mart_monthly", path=demo)) > 0
    frame = query(
        read_sql("promotion_analysis.sql"), {"start": "2025-11-01", "end": "2025-12-31"}, demo
    )
    assert frame.spend.gt(0).all()


def test_failed_publish_retains_database(demo, tmp_path, monkeypatch):
    import hashlib
    from pulse.data import pipeline

    original = hashlib.sha256(demo.read_bytes()).hexdigest()
    invalid = frames(small=True)
    invalid["fact_sales"].loc[0, "location_id"] = 999
    monkeypatch.setattr(pipeline, "write_raw", lambda *a, **k: invalid)
    with pytest.raises(ValueError, match="Validation failed"):
        pipeline.build(
            demo, small=True, raw_path=tmp_path / "raw", report_path=tmp_path / "reports"
        )
    assert hashlib.sha256(demo.read_bytes()).hexdigest() == original


def test_brief_reconciles(demo, tmp_path):
    from pulse.reports.brief import export_reports

    brief = export_reports(demo, tmp_path)
    measured = investigate(*latest_week(demo), path=demo)["after"]
    assert brief["business_health"]["revenue"] == pytest.approx(measured["revenue"])
    assert brief["estimated_weekly_profit_exposure"] == pytest.approx(
        exposure_summary(detect(demo))
    )
    assert "All synthetic" in (tmp_path / "monday_brief.html").read_text()
    assert brief["synthetic"] is True


def test_distinct_customers_and_labour_question(demo):
    from pulse.analytics.core import ledger

    start, end = latest_week(demo)
    count = query(
        "SELECT COUNT(DISTINCT customer_id) FROM fact_sales WHERE customer_id<>0 AND date_id BETWEEN ? AND ?",
        (start, end),
        demo,
    ).iloc[0, 0]
    assert ledger(start, end, path=demo)["customer_count"] == count
    result = answer("Where is labour percentage increasing?", demo)
    assert "change_pp" in result["evidence"]
    assert result["evidence"].change_pp.is_monotonic_decreasing


def test_calendar_completion(demo):
    assert latest_week(demo) == ("2025-12-22", "2025-12-28")
    r = query("SELECT * FROM mart_monthly WHERE location_id=1 ORDER BY month", path=demo)
    assert r.iloc[1].previous_revenue == pytest.approx(r.iloc[0].revenue)
    assert r.iloc[2].rolling_3m_revenue == pytest.approx(r.iloc[:3].revenue.mean())


def test_weekly_promotions_have_historical_reference(demo):
    start, end = latest_week(demo)
    result = query(read_sql("promotion_analysis.sql"), {"start": start, "end": end}, demo)
    assert not result.empty
    assert result.min_reference_days.ge(3).all()


def test_promotion_assignment_contract():
    source = frames(small=True)
    row = source["fact_sales"].iloc[0]
    mask = (source["fact_promotions"].date_id == row.date_id) & (
        source["fact_promotions"].location_id == row.location_id
    )
    source["fact_promotions"].loc[mask, "promotion_id"] = 2
    checks = validate(source).set_index("rule")
    assert checks.loc["promotions: order assignment", "status"] == "FAIL"
