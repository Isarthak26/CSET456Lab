import os
from collections import Counter


SOURCE_EXTENSIONS = {
    ".py": "Python",
}


def count_lines(file_path):
    """Count lines in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return sum(1 for _ in file)
    except (UnicodeDecodeError, PermissionError):
        return 0


def get_repository_inventory(repo_path):
    """Analyze repository structure and source-code metrics."""

    total_files = 0
    total_directories = 0
    source_files = 0
    total_loc = 0

    language_counts = Counter()
    extension_counts = Counter()
    source_file_details = []

    for root, directories, files in os.walk(repo_path):

        # Ignore Git's internal directory
        directories[:] = [d for d in directories if d != ".git"]

        total_directories += len(directories)
        total_files += len(files)

        for file in files:
            file_path = os.path.join(root, file)

            extension = os.path.splitext(file)[1].lower()

            # File-type distribution
            extension_counts[extension or "no_extension"] += 1

            # Source-code analysis
            if extension in SOURCE_EXTENSIONS:
                source_files += 1

                language = SOURCE_EXTENSIONS[extension]
                language_counts[language] += 1

                loc = count_lines(file_path)
                total_loc += loc

                source_file_details.append({
                    "file": os.path.relpath(file_path, repo_path),
                    "loc": loc
                })

    # Sort source files by LOC
    source_file_details.sort(
        key=lambda item: item["loc"],
        reverse=True
    )

    largest_source_files = source_file_details[:5]

    average_loc = (
        total_loc / source_files
        if source_files > 0
        else 0
    )

    return {
        "repository_name": os.path.basename(repo_path),
        "total_files": total_files,
        "source_code_files": source_files,
        "total_directories": total_directories,
        "total_loc": total_loc,
        "average_loc_per_source_file": round(average_loc, 2),
        "language_distribution": dict(language_counts),
        "file_type_distribution": dict(extension_counts),
        "largest_source_files": largest_source_files
    }


if __name__ == "__main__":
    repo_path = os.path.expanduser(
        "~/repository_mining/requests"
    )

    inventory = get_repository_inventory(repo_path)

    print(inventory)