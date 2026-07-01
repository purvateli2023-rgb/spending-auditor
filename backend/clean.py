import pandas as pd

# Load the raw CSV
df = pd.read_csv("transactions.csv")

# Rename YOUR columns to standard names
df = df.rename(columns={
    "Date": "date",
    "Transaction Description": "description",
    "Amount": "amount"
})

# Keep only the 3 columns we need
df = df[["date", "description", "amount"]]

# Clean the amount column — remove $ signs and commas if present
df["amount"] = (
    df["amount"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# Make all amounts positive
df["amount"] = df["amount"].abs()

# Convert date to proper format
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Drop rows where date couldn't be read
df = df.dropna(subset=["date"])

# Print summary
print(f"Total transactions: {len(df)}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Total amount: ${df['amount'].sum():.2f}")
print("\nFirst 5 cleaned rows:")
print(df.head())

# Save cleaned version
df.to_csv("cleaned.csv", index=False)
print("\n✅ Saved cleaned.csv")