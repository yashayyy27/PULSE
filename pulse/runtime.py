"""Local configuration and read-only query boundary."""

import json
import os
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def settings():
    return json.loads((ROOT / "config/settings.json").read_text())


def database_path():
    return Path(os.environ.get("PULSE_DB", str(ROOT / "data/pulse.sqlite")))


def connect(path=None):
    """Analytics never execute user SQL; use a read-only connection."""
    target = Path(path or database_path()).resolve()
    connection = sqlite3.connect(f"file:{target.as_posix()}?mode=ro", uri=True)
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def query(sql, params=(), path=None):
    with connect(path) as connection:
        return pd.read_sql_query(sql, connection, params=params)


def read_sql(name):
    return (ROOT / "sql" / name).read_text()
