import json
import csv

# Load JSON file
with open("python_errors_10k.json", "r") as f:
    data = json.load(f)

# Write CSV
with open("output.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["code","error_type","error_message","category"])
    writer.writeheader()
    writer.writerows(data)

print("CSV file created successfully!")