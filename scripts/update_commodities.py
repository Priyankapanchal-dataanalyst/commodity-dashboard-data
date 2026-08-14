import csv
import json
import os
from datetime import datetime, timezone, timedelta

import requests


BASE_URL = "https://croncopia.com/api/metals/"

COMMODITIES = [
    ("Gold", "gold"),
    ("Silver", "silver"),
    ("Platinum", "platinum"),
    ("Palladium", "palladium"),
    ("Copper", "copper"),
    ("Aluminum", "aluminum"),
    ("Cobalt", "colbalt"),
    ("Gallium", "gallium"),
    ("Indium", "indium"),
    ("Iridium", "iridium"),
    ("Iron Ore", "iron"),
    ("Lead", "lead"),
    ("Lithium Carbonate", "lithium"),
    ("Molybdenum", "molybdenum"),
    ("Neodymium", "neodymium"),
    ("Nickel", "nickel"),
    ("Rhodium", "rhodium"),
    ("Ruthenium", "ruthenium"),
    ("Tellurium", "tellurium"),
    ("Tin", "tin"),
    ("Uranium (U3O8)", "uranium"),
    ("Zinc", "zinc"),
    ("Steel (HRC)", "steal"),
]

CSV_FILE = "data/commodity_history.csv"

# Date used for the daily snapshot
today = datetime.now(timezone.utc).date().isoformat()

rows = []

for commodity_name, slug in COMMODITIES:
    url = f"{BASE_URL}{slug}.json"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    usd_per_kg = data["price"]["kilogram"]
    timestamp = data["timestamp"]

    rows.append({
        "Snapshot_Date": today,
        "Croncopia_Timestamp": timestamp,
        "Commodity_Name": commodity_name,
        "USD_Per_KG": usd_per_kg
    })


# Read existing history
existing_rows = []

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_rows = list(reader)


# Add today's snapshot
all_rows = existing_rows + rows


# Keep only the most recent 30 days
cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=29)

filtered_rows = [
    row
    for row in all_rows
    if row["Snapshot_Date"]
    and datetime.strptime(
        row["Snapshot_Date"], "%Y-%m-%d"
    ).date() >= cutoff_date
]


# Remove duplicate commodity records for the same day
unique_rows = {}

for row in filtered_rows:
    key = (row["Snapshot_Date"], row["Commodity_Name"])
    unique_rows[key] = row


filtered_rows = list(unique_rows.values())

# Sort by date and commodity
filtered_rows.sort(
    key=lambda x: (x["Snapshot_Date"], x["Commodity_Name"])
)


# Write updated CSV
with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "Snapshot_Date",
        "Croncopia_Timestamp",
        "Commodity_Name",
        "USD_Per_KG"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(filtered_rows)


print(f"Updated {CSV_FILE}")
print(f"Total records: {len(filtered_rows)}")
print(f"Today's records: {len(rows)}")
