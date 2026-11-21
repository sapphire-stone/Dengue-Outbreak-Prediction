import pandas as pd

df = pd.read_csv("data/dengue_data.csv")
print("Columns:", list(df.columns))
print("Rows & Cols:", df.shape)
print("Missing values:\n", df.isna().sum())
print("Unique wards:", df["ward_id"].nunique())
print(df.head(3))