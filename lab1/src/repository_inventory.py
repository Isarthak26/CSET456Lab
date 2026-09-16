import os


def get_repository_inventory(repo_path):
    """Count files and directories in a repository."""
    total_files = 0
    total_directories = 0

    for root, directories, files in os.walk(repo_path):
        # Do not include Git's internal directory
        directories[:] = [d for d in directories if d != ".git"]

        total_directories += len(directories)
        total_files += len(files)

    return {
        "repository_name": os.path.basename(repo_path),
        "total_files": total_files,
        "total_directories": total_directories
    }
if __name__ == "__main__":
    repo_path = os.path.expanduser("~/repository_mining/requests")

    inventory = get_repository_inventory(repo_path)

    print(inventory)
