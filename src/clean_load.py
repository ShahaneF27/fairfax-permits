import pandas as pd

RAW_PATH = "data/raw/building_records_plus.csv"

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