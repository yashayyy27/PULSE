"""Full local audit: independent source totals, all scopes, engines and app pages."""

import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from streamlit.testing.v1 import AppTest
from app.components import PAGES
from pulse.analytics.core import DIMENSIONS, contributions, daily, investigate, latest_week, ledger
from pulse.alerts.engine import detect, exposure_summary
from pulse.forecasting.engine import forecast
from pulse.query.ask import EXAMPLES, answer
from pulse.runtime import ROOT, database_path, query
from pulse.scenarios.engine import simulate


def main():
    started = perf_counter()
    metadata = dict(query("SELECT * FROM metadata").itertuples(index=False, name=None))
    source = query(
        "SELECT SUM(list_sales-discount-refund) revenue,SUM(cogs) cogs,SUM(channel_fee) fees FROM fact_sales"
    ).iloc[0]
    payroll = query("SELECT SUM(labour_cost) costs FROM fact_labour").iloc[0, 0]
    overhead = query("SELECT SUM(overhead) costs FROM fact_operating_costs").iloc[0, 0]
    campaign = query("SELECT SUM(campaign_spend) costs FROM fact_promotions").iloc[0, 0]
    profit = source.revenue - source.cogs - source.fees - payroll - overhead - campaign
    measured = ledger(metadata["start"], metadata["end"])
    assert abs(measured["revenue"] - source.revenue) < 0.01
    assert abs(measured["operating_profit"] - profit) < 0.01
    scope_results = []
    start, end = latest_week()
    for location in [None, *query("SELECT location_id FROM dim_location").location_id.tolist()]:
        inv = investigate(start, end, location)
        assert (
            abs(
                inv["bridge"].impact.sum()
                - (inv["after"]["operating_profit"] - inv["before"]["operating_profit"])
            )
            < 0.001
        )
        assert (
            abs(simulate(inv["after"])["operating_profit"] - inv["after"]["operating_profit"])
            < 0.001
        )
        scope_results.append(
            {"location_id": location, "profit_bridge": "PASS", "scenario_identity": "PASS"}
        )
    company = investigate(start, end)
    for dimension in DIMENSIONS:
        out = contributions(start, end, dimension)
        assert (
            abs(
                out.contribution.sum()
                - (company["after"]["revenue"] - company["before"]["revenue"])
            )
            < 0.001
        )
    alert_started = perf_counter()
    alerts = detect()
    alert_seconds = perf_counter() - alert_started
    for q in EXAMPLES:
        assert answer(q)["supported"]
    fc = forecast(daily())
    assert np.isfinite(fc["future"].forecast).all()
    page_results = []
    for page in PAGES:
        tick = perf_counter()
        app = AppTest.from_file(str(ROOT / "app/main.py"), default_timeout=60)
        app.session_state["nav"] = page
        app.run()
        assert not app.exception, (page, [item.message for item in app.exception])
        page_results.append(
            {
                "page": page,
                "status": "PASS",
                "seconds": round(perf_counter() - tick, 3),
                "charts": len(app.get("plotly_chart")),
                "tables": len(app.dataframe),
            }
        )
    manifest = json.loads((ROOT / "reports/pipeline.json").read_text())
    for name, digest in manifest["raw_sha256"].items():
        assert (
            hashlib.sha256((ROOT / "data/raw" / f"{name}.csv.gz").read_bytes()).hexdigest()
            == digest
        )
    out = {
        "metadata": metadata,
        "source_reconciliation": "PASS",
        "scopes": scope_results,
        "dimensions": len(DIMENSIONS),
        "pages": page_results,
        "alerts": len(alerts),
        "estimated_weekly_profit_exposure": exposure_summary(alerts),
        "alert_seconds": round(alert_seconds, 3),
        "total_seconds": round(perf_counter() - started, 3),
        "db_bytes": database_path().stat().st_size,
        "forecast_holdout": fc["metrics"].to_dict("records"),
        "raw_hash_check": "PASS",
    }
    (ROOT / "reports/full_verification.json").write_text(json.dumps(out, indent=2, allow_nan=False))
    print(
        f"PASS: {metadata['orders']} orders, {len(scope_results)} scopes, {len(DIMENSIONS)} dimensions, {len(page_results)} app views"
    )


if __name__ == "__main__":
    main()
