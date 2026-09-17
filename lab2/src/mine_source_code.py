import csv
import os

from repositories import REPOSITORIES


BASE_DIR = "lab2_repositories"
OUTPUT_FILE = "lab2/data/source_code_raw.csv"

SOURCE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
}


def count_loc(file_path):
    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:
            return sum(1 for line in f if line.strip())

    except Exception:
        return 0


rows = []


for repo_url in REPOSITORIES:

    # Extract repository name from GitHub URL
    repo_name = repo_url.rstrip("/").split("/")[-1]

    # Local repository directory
    repo_path = os.path.join(BASE_DIR, repo_name)

    if not os.path.exists(repo_path):
        print(f"Repository not found: {repo_name}")
        continue

    print(f"Mining: {repo_name}")

    for root, _, files in os.walk(repo_path):

        for file_name in files:

            extension = os.path.splitext(file_name)[1].lower()

            # Ignore non-source files
            if extension not in SOURCE_EXTENSIONS:
                continue

            file_path = os.path.join(root, file_name)

            relative_path = os.path.relpath(
                file_path,
                repo_path
            )

            loc = count_loc(file_path)

            size_bytes = os.path.getsize(file_path)

            rows.append({
                "repository": repo_name,
                "file_path": relative_path,
                "language": SOURCE_EXTENSIONS[extension],
                "extension": extension,
                "loc": loc,
                "size_bytes": size_bytes
            })


# Create data directory if it does not exist
os.makedirs("lab2/data", exist_ok=True)


# Write CSV
with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

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
    writer.writerows(rows)


print("\nSource-code mining completed.")
print(f"Total source files: {len(rows)}")
print(f"Saved to: {OUTPUT_FILE}")