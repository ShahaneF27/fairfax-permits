import pandas as pd

#1. load the CSV into a DataFrame (a table in mem)
df = pd.read_csv("data/raw/building_records_plus.csv", low_memory=False)
df.columns = df.columns.str.strip().str.rstrip(":")

#2. how big is it
print("Rows, columns:", df.shape)

#3. what are the columns, and how many values are missing in each
print("\n--- Columns and missing values ---")
summary = pd.DataFrame({
    "non_null": df.notna().sum(),
    "missing": df.isna().sum(),
    "dtype": df.dtypes,
})
print(summary.to_string())

#4. is each permit listed once or are there duplicates
print("\nUnique Record IDs:", df["Record ID"].nunique())      

#5. what categories exist
for col in ["Record type", "Record status", "Supervisor district"]:
    print(f"\n--- {col} ---")
    print(df[col].value_counts(dropna=False).to_string())

#6. peek at a few date values
print("\n--- Sample dates ---")
print(df["Submitted date"].head(5).to_string())    

#7. which record types are missing dates
print("\n--- % of each date missing, by record type ---")
date_cols = ["Submitted date", "Accepted date", "Issued date", "Approved date", "Closed date"]
missing_by_type = df[date_cols].isna().groupby(df["Record type"]).mean() * 100
print(missing_by_type.round(1).to_string())