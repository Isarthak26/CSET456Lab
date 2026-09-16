import os
import csv
from repositories import REPOSITORIES

REPO_DIR = os.path.expanduser("~/repository_mining/lab2_repositories")
OUTPUT_FILE = "data/source_code_raw.csv"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

records = []

for repo_url in REPOSITORIES:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = os.path.join(REPO_DIR, repo_name)

    print(f"Mining {repo_name}...")

    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                records.append({
                    "repository": repo_name,
                    "file_path": os.path.relpath(file_path, repo_path),
                    "language": "Python",
                    "extension": ".py",
                    "loc": len(lines),
                    "size_bytes": os.path.getsize(file_path)
                })

            except (UnicodeDecodeError, OSError):
                continue

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "repository",
            "file_path",
            "language",
            "extension",
            "loc",
            "size_bytes"
        ]
    )

    writer.writeheader()
    writer.writerows(records)

print(f"\nSource-code dataset created: {OUTPUT_FILE}")
print(f"Total source files: {len(records)}")