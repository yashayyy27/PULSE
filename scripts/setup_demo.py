"""Reproduce source, star schema, marts, analytics and evidence exports."""

import argparse
import json
from time import perf_counter
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pulse.data.pipeline import build
from pulse.runtime import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--small", action="store_true", help="Six stores, 210 days for CI")
    parser.add_argument("--db", type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    started = perf_counter()
    result = build(args.db, args.small)
    print(
        f"Synthetic pipeline complete: {result['orders']} orders; {result['validation_rules']} checks"
    )
    from pulse.reports.brief import export_reports

    export_reports(args.db)
    (ROOT / "reports/setup_timing.json").write_text(
        json.dumps(
            {
                "seconds": round(perf_counter() - started, 3),
                "small": args.small,
                "orders": result["orders"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
