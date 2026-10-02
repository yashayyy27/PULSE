import pytest
from pulse.data.pipeline import build
from pulse.analytics.core import ledger, latest_week


@pytest.fixture(scope="session")
def demo(tmp_path_factory):
    root = tmp_path_factory.mktemp("pipeline")
    db = root / "sample.sqlite"
    build(db, small=True, raw_path=root / "raw", report_path=root / "reports")
    return db


@pytest.fixture
def baseline(demo):
    return ledger(*latest_week(demo), path=demo)
