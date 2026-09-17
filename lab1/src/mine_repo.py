import os
import subprocess


def clone_repository(repo_url, repo_path):
    if not os.path.exists(repo_path):
        print("Cloning repository...")
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    else:
        print("Repository already exists.")


def get_repo_inventory(repo_path):
    total_files = 0
    total_directories = 0

    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")

        total_directories += len(dirs)
        total_files += len(files)

    return total_files, total_directories


def count_python_files(repo_path):
    python_files = 0

    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            if file.endswith(".py"):
                python_files += 1

    return python_files


repo_url = "https://github.com/psf/requests.git"
repo_path = "requests"

clone_repository(repo_url, repo_path)

files, directories = get_repo_inventory(repo_path)
python_files = count_python_files(repo_path)

print("\nRepository Inventory")
print("--------------------")
print("Total files:", files)
print("Total directories:", directories)
print("Python source files:", python_files)
