import csv
import os
from datetime import datetime


INPUT_FILE = "lab2/data/commit_history_raw.csv"
OUTPUT_FILE = "lab2/data/commit_history_clean.csv"


rows = []
seen_commits = set()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        repository = row["repository"].strip()
        commit_hash = row["commit_hash"].strip()
        date = row["date"].strip()

        if not repository or not commit_hash:
            continue

        # A commit hash should be unique within a repository
        key = (repository, commit_hash)

        if key in seen_commits:
            continue

        # Validate date
        try:
            datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            continue

        # Validate numeric fields
        try:
            row["files_changed"] = int(row["files_changed"])
            row["insertions"] = int(row["insertions"])
            row["deletions"] = int(row["deletions"])
        except ValueError:
            continue

        seen_commits.add(key)
        rows.append(row)


os.makedirs("lab2/data", exist_ok=True)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    fieldnames = [
        "repository",
        "commit_hash",
        "author",
        "date",
        "message",
        "files_changed",
        "insertions",
        "deletions"
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(rows)


print("Commit-history cleaning completed.")
print("Rows before cleaning: 77927")
print(f"Rows after cleaning: {len(rows)}")
print(f"Removed rows: {77927 - len(rows)}")
print(f"Saved to: {OUTPUT_FILE}")