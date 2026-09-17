import csv
from collections import defaultdict


INPUT_FILE = "lab2/data/commit_history_clean.csv"
OUTPUT_FILE = "lab2/data/commit_summary.csv"


stats = defaultdict(
    lambda: {
        "total_commits": 0,
        "total_files_changed": 0,
        "total_insertions": 0,
        "total_deletions": 0,
    }
)


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        repo = row["repository"]

        stats[repo]["total_commits"] += 1
        stats[repo]["total_files_changed"] += int(row["files_changed"])
        stats[repo]["total_insertions"] += int(row["insertions"])
        stats[repo]["total_deletions"] += int(row["deletions"])


rows = []

for repo, values in stats.items():

    commits = values["total_commits"]

    rows.append({
        "repository": repo,
        "total_commits": commits,
        "total_files_changed": values["total_files_changed"],
        "total_insertions": values["total_insertions"],
        "total_deletions": values["total_deletions"],
        "avg_files_changed_per_commit":
            round(values["total_files_changed"] / commits, 2),
        "avg_insertions_per_commit":
            round(values["total_insertions"] / commits, 2),
        "avg_deletions_per_commit":
            round(values["total_deletions"] / commits, 2),
    })


with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    fieldnames = [
        "repository",
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


print("Commit summary created.")
print(f"Repositories: {len(rows)}")
print(f"Saved to: {OUTPUT_FILE}")