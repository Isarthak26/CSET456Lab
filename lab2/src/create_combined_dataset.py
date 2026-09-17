import csv
import os
from collections import defaultdict


SOURCE_FILE = "lab2/data/source_code_clean.csv"
COMMIT_FILE = "lab2/data/commit_summary.csv"
OUTPUT_FILE = "lab2/data/combined_repository_dataset.csv"


source_stats = defaultdict(
    lambda: {
        "total_source_files": 0,
        "total_loc": 0,
        "total_size_bytes": 0,
    }
)


with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        repo = row["repository"]

        source_stats[repo]["total_source_files"] += 1
        source_stats[repo]["total_loc"] += int(row["loc"])
        source_stats[repo]["total_size_bytes"] += int(row["size_bytes"])


commit_stats = {}

with open(COMMIT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        commit_stats[row["repository"]] = row


rows = []

for repo in source_stats:

    source = source_stats[repo]
    commit = commit_stats[repo]

    total_files = source["total_source_files"]

    rows.append({
        "repository": repo,
        "total_source_files": total_files,
        "total_loc": source["total_loc"],
        "total_size_bytes": source["total_size_bytes"],
        "avg_loc_per_file": round(
            source["total_loc"] / total_files, 2
        ),
        "total_commits": int(commit["total_commits"]),
        "total_files_changed": int(commit["total_files_changed"]),
        "total_insertions": int(commit["total_insertions"]),
        "total_deletions": int(commit["total_deletions"]),
        "avg_files_changed_per_commit": float(
            commit["avg_files_changed_per_commit"]
        ),
        "avg_insertions_per_commit": float(
            commit["avg_insertions_per_commit"]
        ),
        "avg_deletions_per_commit": float(
            commit["avg_deletions_per_commit"]
        ),
    })


os.makedirs("lab2/data", exist_ok=True)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    fieldnames = [
        "repository",
        "total_source_files",
        "total_loc",
        "total_size_bytes",
        "avg_loc_per_file",
        "total_commits",
        "total_files_changed",
        "total_insertions",
        "total_deletions",
        "avg_files_changed_per_commit",
        "avg_insertions_per_commit",
        "avg_deletions_per_commit",
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(rows)


print("Combined repository dataset created.")
print(f"Repositories: {len(rows)}")
print(f"Saved to: {OUTPUT_FILE}")