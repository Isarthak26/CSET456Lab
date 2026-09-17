import csv
import subprocess
from repositories import REPOSITORIES

BASE_DIR = "lab2_repositories"
OUTPUT_FILE = "lab2/data/commit_history_raw.csv"


def get_repo_name(url):
    return url.rstrip("/").split("/")[-1].replace(".git", "")


def mine_repository(repo_path, repo_name, writer):
    command = [
        "git",
        "-C",
        repo_path,
        "log",
        "--all",
        "--date=iso",
        "--pretty=format:%H|%an|%ad|%s",
        "--numstat",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    lines = result.stdout.splitlines()

    current_commit = None
    current_author = None
    current_date = None
    current_message = None
    files_changed = 0
    insertions = 0
    deletions = 0

    def write_commit():
        if current_commit:
            writer.writerow({
                "repository": repo_name,
                "commit_hash": current_commit,
                "author": current_author,
                "date": current_date,
                "message": current_message,
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
            })

    for line in lines:
        if "|" in line and not line.startswith((" ", "\t")):
            write_commit()

            parts = line.split("|", 3)

            if len(parts) == 4:
                current_commit = parts[0]
                current_author = parts[1]
                current_date = parts[2]
                current_message = parts[3]

                files_changed = 0
                insertions = 0
                deletions = 0

        elif line.strip():
            parts = line.split("\t")

            if len(parts) == 3:
                added, deleted, _ = parts

                try:
                    insertions += int(added)
                except ValueError:
                    pass

                try:
                    deletions += int(deleted)
                except ValueError:
                    pass

                files_changed += 1

    write_commit()


with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "repository",
        "commit_hash",
        "author",
        "date",
        "message",
        "files_changed",
        "insertions",
        "deletions",
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for url in REPOSITORIES:
        repo_name = get_repo_name(url)
        repo_path = f"{BASE_DIR}/{repo_name}"

        print(f"Mining commit history: {repo_name}...")
        mine_repository(repo_path, repo_name, writer)

print(f"\nCommit-history dataset created: {OUTPUT_FILE}")
