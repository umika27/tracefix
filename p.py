import json
import csv
import re


with open("tracefix_25k_dataset.json", "r") as f:
    data = json.load(f)

# Label mapping (standardization)
LABEL_MAP = {
    "TypeError": "TypeError",
    "NameError": "Dependency",
    "ModuleNotFoundError": "Dependency",
    "ImportError": "Dependency",
    "IndexError": "IndexError",
    "KeyError": "KeyError",
    "SyntaxError": "SyntaxError",
    "IndentationError": "SyntaxError",
    "FileNotFoundError": "Dependency",
    "AttributeError": "TypeError",
    "ZeroDivisionError": "TypeError"
}

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text) 
    text = re.sub(r'[^a-z0-9\s]', '', text) 
    return text.strip()

cleaned_data = []
seen = set()

for item in data:
    output = item["output"]

    # Extract fields
    try:
        error_type = re.search(r"📌 Type\s*:\s*(.*)", output).group(1).strip()
        cause = re.search(r"⚠️ Cause\s*:\s*(.*)", output).group(1).strip()
        fix = re.search(r"🛠️ Fix\s*:\s*(.*)", output).group(1).strip()
    except:
        continue

    # Standardize label
    label = LABEL_MAP.get(error_type, None)
    if not label:
        continue

    # Normalize
    error_message = normalize_text(cause)
    fix = normalize_text(fix)

    # Remove duplicates
    key = (error_message, label, fix)
    if key in seen:
        continue
    seen.add(key)

    cleaned_data.append({
        "errormessage": error_message,
        "label": label,
        "fix": fix
    })

# Save CSV
with open("cleaned_dataset.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["errormessage", "label", "fix"])
    writer.writeheader()
    writer.writerows(cleaned_data)

print(f"✅ Done! Clean dataset saved with {len(cleaned_data)} rows.")