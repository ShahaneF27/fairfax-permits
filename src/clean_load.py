import pandas as pd
import sqlite3

RAW_PATH = "data/raw/building_records_plus.csv"
DB_PATH = "data/permits.db"
SCHEMA_PATH = "sql/schema.sql"

#1.load
df = pd.read_csv(RAW_PATH, low_memory=False)
df.columns = df.columns.str.strip().str.rstrip(":")

#2. rename columns to snake_case
df.columns = df.columns.str.lower().str.replace(" ", "_")

#3. drop columns that are not needed
DROP_COLS = [
    "document_url", "globalid", "objectid", "created_user",
    "created_date", "last_edited_user", "last_edited_date",
    "shape__area", "shape__length", "public_view", "more_info",
]
df = df.drop(columns=DROP_COLS)

#4. convert data text into real dates
DATE_COLS = [
    "status_date", "submitted_date", "accepted_date", "issued_date",
    "approved_date", "closed_date",
]
for col in DATE_COLS:
    before = df[col].notna().sum()
    df[col] = pd.to_datetime(df[col], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    after = df[col].notna().sum()
    print(f"{col}: {before} values in, {after} converted")

#5. drop rows with no supervisor district
before = len(df)
df = df.dropna(subset=["supervisor_district"])
print(f"\nDropped {before - len(df)} rows with no supervisor district")

#6. tidy text fields
df["parcel_id_number"] = df["parcel_id_number"].str.split().str.join(" ")
df["zip5"] = df["zip_code"].str[:5]
df["supervisor_district"] = df["supervisor_district"].str.title()

#7.category and sector
CATEGORY_MAP = {
    "Residential New": "Construction",
    "Residential Addition/Alteration": "Construction",
    "Commercial New": "Construction",
    "Commercial Addition/Alteration": "Construction",
    "Certificate of Occupancy (Non-RUP)": "Business Occupancy",
    "Certificate of Occupancy": "Certificate of Occupancy",
}
SECTOR_MAP = {
    "Residential New": "Residential",
    "Residential Addition/Alteration": "Residential",
    "Commercial New": "Commercial",
    "Commercial Addition/Alteration": "Commercial",
    "Certificate of Occupancy (Non-RUP)": "Commercial",
    "Certificate of Occupancy": "Unspecified",
}
df["category"] = df["record_type"].map(CATEGORY_MAP)
df["sector"] = df["record_type"].map(SECTOR_MAP)

#8. processing time
is_construction = df["category"] == "Construction"
is_business = df["category"] == "Business Occupancy"

df["decision_date"] = (
    df["issued_date"].where(is_construction)
    .fillna(df["approved_date"].where(is_business))
)
df["days_to_decision"] = (df["decision_date"] - df["submitted_date"]).dt.days

negative = df["days_to_decision"] < 0
print(f"Negative processing times removed: {negative.sum()}")
df["days_to_decision"] = df["days_to_decision"].mask(negative)

# ---------- 9. Flags ----------
df["is_open"] = df["closed_date"].isna().astype(int)
df["in_growth_center"] = df["development_center"].notna().astype(int)

#check work
print("\nRows:", len(df))
print("\n--- Records by category and sector ---")
print(df.groupby(["category", "sector"]).size().to_string())
print("\n--- Median days to decision, by record type ---")
print(df.groupby("record_type")["days_to_decision"].median().to_string())
print("\nShare still open:", round(df["is_open"].mean() * 100, 1), "%")
print("Share in a growth center:", round(df["in_growth_center"].mean() * 100, 1), "%")

#10. build lookup tables
record_types = (
    df[["record_type", "category", "sector"]]
    .drop_duplicates()
    .sort_values("record_type")
    .reset_index(drop=True)
)
record_types["record_type_id"] = record_types.index + 1

districts = pd.DataFrame({"district_name": sorted(df["supervisor_district"].unique())})
districts["district_id"] = districts.index + 1

growth_centers = pd.DataFrame({"growth_center_name": sorted(df["development_center"].dropna().unique())})
growth_centers["growth_center_id"] = growth_centers.index + 1

#11. swap names for IDs in the permits table
permits = (
    df.merge(record_types[["record_type", "record_type_id"]], on="record_type", how="left")
      .merge(districts, left_on="supervisor_district", right_on="district_name", how="left")
      .merge(growth_centers, left_on="development_center", right_on="growth_center_name", how="left")
)
permits["growth_center_id"] = permits["growth_center_id"].astype("Int64")
permits["days_to_decision"] = permits["days_to_decision"].astype("Int64")

for col in DATE_COLS:
    permits[col] = permits[col].dt.strftime("%Y-%m-%d")

permits = permits.rename(columns={"parcel_id_number": "parcel_id"})
PERMIT_COLS = [
    "record_id", "record_type_id", "district_id", "growth_center_id",
    "project_name", "parcel_id", "address", "city", "zip5", "record_status",
    "status_date", "submitted_date", "accepted_date", "issued_date",
    "approved_date", "closed_date", "days_to_decision", "is_open",
]
permits = permits[PERMIT_COLS]

#12. write to SQLite
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    record_types[["record_type_id", "record_type", "category", "sector"]].to_sql(
        "record_types", conn, if_exists="append", index=False)
    districts[["district_id", "district_name"]].to_sql(
        "districts", conn, if_exists="append", index=False)
    growth_centers[["growth_center_id", "growth_center_name"]].to_sql(
        "growth_centers", conn, if_exists="append", index=False)
    permits.to_sql("permits", conn, if_exists="append", index=False)

    # Verify the load
    print("\n--- Database check ---")
    for table in ["record_types", "districts", "growth_centers", "permits"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count} rows")
    problems = conn.execute("PRAGMA foreign_key_check").fetchall()
    print("Foreign key problems:", len(problems))