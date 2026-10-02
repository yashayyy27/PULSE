"""Validate then atomically publish the constrained analytical database."""

import hashlib
import json
import logging
import sqlite3
from pathlib import Path

from pulse.data.generator import write_raw
from pulse.data.validation import validate
from pulse.runtime import ROOT, settings

LOGGER = logging.getLogger(__name__)


def build(path=None, small=False, seed=None, raw_path=None, report_path=None):
    path = Path(path or ROOT / "data/pulse.sqlite")
    raw = Path(raw_path or ROOT / "data/raw")
    reports = Path(report_path or ROOT / "reports")
    reports.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Generating synthetic source: small=%s", small)
    seed = settings()["seed"] if seed is None else seed
    tables = write_raw(raw, seed, small)
    checks = validate(tables)
    checks.to_csv(reports / "data_quality.csv", index=False)
    if (checks.status == "FAIL").any():
        raise ValueError("Validation failed; previous database retained. See data_quality.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.with_suffix(".building")
    staged.unlink(missing_ok=True)
    try:
        with sqlite3.connect(staged) as con:
            con.executescript((ROOT / "sql/schema.sql").read_text())
            for name, frame in tables.items():
                # pandas append preserves the declared constraints and FK enforcement.
                frame.to_sql(name, con, index=False, if_exists="append", chunksize=10000)
            fk = con.execute("PRAGMA foreign_key_check").fetchall()
            if fk:
                raise ValueError(f"Broken foreign keys: {fk[:3]}")
            con.executescript((ROOT / "sql/transform.sql").read_text())
            raw_revenue = con.execute(
                "SELECT SUM(list_sales-discount-refund) FROM fact_sales"
            ).fetchone()[0]
            mart_revenue = con.execute("SELECT SUM(revenue) FROM mart_daily").fetchone()[0]
            if abs(raw_revenue - mart_revenue) > 0.01:
                raise ValueError("Revenue reconciliation failed")
            checks.to_sql("quality_checks", con, index=False)
            con.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
            metadata = {
                "synthetic": "true",
                "seed": str(seed),
                "small": str(small),
                "start": str(tables["dim_date"].date_id.min()),
                "end": str(tables["dim_date"].date_id.max()),
                "orders": str(len(tables["fact_sales"])),
                "locations": str(len(tables["dim_location"])),
            }
            con.executemany("INSERT INTO metadata VALUES(?,?)", metadata.items())
            con.commit()
        staged.replace(path)
    except Exception:
        staged.unlink(missing_ok=True)
        raise
    manifests = {
        name: hashlib.sha256((raw / f"{name}.csv.gz").read_bytes()).hexdigest() for name in tables
    }
    output = {
        **metadata,
        "raw_sha256": manifests,
        "validation_rules": len(checks),
        "validation_failures": int(checks.failures.sum()),
        "revenue_reconciliation": abs(raw_revenue - mart_revenue),
    }
    (reports / "pipeline.json").write_text(json.dumps(output, indent=2))
    LOGGER.info("Published %s orders; %s validation rules", metadata["orders"], len(checks))
    return output
