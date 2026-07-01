import pandas as pd

df = pd.read_csv("transactions.csv")

print("First 5 rows:")
print(df.head())

print("\nColumn names:")
print(df.columns.tolist())