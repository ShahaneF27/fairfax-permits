import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "data/permits.db"
OUT_DIR = Path("dashboard/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERIES = {
    "permits": """
        SELECT *
        FROM permits
        WHERE submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
    """,
    "record_types": "SELECT * FROM record_types",
    "districts": "SELECT * FROM districts",
    "growth_centers": "SELECT * FROM growth_centers",
}

with sqlite3.connect(DB_PATH) as conn:
    for name, sql in QUERIES.items():
        df = pd.read_sql_query(sql, conn)
        df.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows -> {OUT_DIR / (name + '.csv')}")
        