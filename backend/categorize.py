import pandas as pd
from transformers import pipeline

# Load the cleaned data
df = pd.read_csv("cleaned.csv")

categories = [
    "Groceries",
    "Subscriptions",
    "Dining and Restaurants",
    "Transport and Gas",
    "Entertainment",
    "Utilities and Bills",
    "Shopping and Clothing",
    "Health and Pharmacy",
    "Other"
]

print("Loading AI model... (first time downloads ~1.6GB, be patient)")
classifier = pipeline(
    "zero-shot-classification",
    model="cross-encoder/nli-MiniLM2-L6-H768"
)
print("✅ Model loaded!")

def get_category(description):
    try:
        result = classifier(str(description), categories)
        return result["labels"][0]
    except:
        return "Other"

# Test on 5 rows first
print("\nTesting on 5 transactions...")
test = df.head(5).copy()
test["category"] = test["description"].apply(get_category)
print(test[["description", "amount", "category"]])

# Ask before running on everything
print("\n---")
go = input("Type 'yes' to categorize ALL 1500 transactions, or 'no' to stop: ")

if go.lower() == "yes":
    print(f"\nCategorizing all {len(df)} transactions... grab a coffee, this takes ~10 mins.")
    df["category"] = df["description"].apply(get_category)
    df.to_csv("categorized.csv", index=False)
    print("\n✅ Done! Saved categorized.csv")
    print("\nCategory breakdown:")
    print(df["category"].value_counts())
else:
    print("Stopped.")
