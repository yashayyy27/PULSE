> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.

# Assumptions and constraints

AUD excluding GST; synthetic orders feature one SKU with multiple units. Returns reverse revenue but do not reverse recorded product cost. Loaded hourly payroll includes on-costs in fictional rates. Overhead excludes depreciation, tax, financing and central office allocations. Inventory is a daily availability snapshot, not units lost or outage duration. Feedback is voluntary and biased. Customer ID 0 is a guest, never one persistent customer.

Two years permit weekly and monthly comparisons, but do not validate business seasonality in the real world. The generator uses annual seasonality rather than an authoritative holiday calendar. Forecast intervals have only three calibration origins; show actual held-out coverage. Promotion references are observational same-store/weekdays. First-observed cohorts are left-censored; latest-month next-month retention is right-censored.

Financial alert gaps are references, not recovered profit. Stockout opportunities assume substitution and minimum matched sample size; do not sum with warning exposures. Scenarios hold specified cost/mix factors fixed and require explicit demand response; retention uses repeat-customer share as a disclosed proxy.

Local SQLite, no credentials and session-only decision/scenario exports constrain this release. No production SLA, access control or native approval workflow is claimed. Dependencies and full generation commands appear in [README](../../README.md); [decision log](29-decision-log.md) explains choices.
