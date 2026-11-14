import sqlite3
import sys

import pandas as pd

DB_PATH = "data/permits.db"

#make sure a query file was provided
if len(sys.argv) != 2:
    print("Usage: python src/run_query.py queries/<file>.sql")
    sys.exit(1)

#read the SQL from the file
query_path = sys.argv[1]
with open(query_path) as f:
    sql = f.read()

#run it and print result
with sqlite3.connect(DB_PATH) as conn:
    result = pd.read_sql_query(sql, conn)

print(result.to_string(index=False))
print(f"\n{len(result)} row)")

