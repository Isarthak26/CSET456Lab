import csv
import os


INPUT_FILE = "lab2/data/source_code_raw.csv"
OUTPUT_FILE = "lab2/data/source_code_clean.csv"


rows = []
seen = set()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        if not row["file_path"].strip():
            continue

        try:
            row["loc"] = int(row["loc"])
            row["size_bytes"] = int(row["size_bytes"])
        except ValueError:
            continue

        key = (
            row["repository"],
            row["file_path"]
        )

        if key in seen:
            continue

        seen.add(key)
        rows.append(row)


os.makedirs("lab2/data", exist_ok=True)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    fieldnames = [
        "repository",
        "file_path",
        "language",
        "extension",
        "loc",
        "size_bytes"
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(rows)


print("Source-code cleaning completed.")
print(f"Rows before cleaning: 2594")
print(f"Rows after cleaning: {len(rows)}")
print(f"Removed rows: {2594 - len(rows)}")
print(f"Saved to: {OUTPUT_FILE}")