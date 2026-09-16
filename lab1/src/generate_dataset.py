import os
import csv

from repository_inventory import (
    get_repository_inventory
)


if __name__ == "__main__":

    repo_path = os.path.expanduser(
        "~/repository_mining/requests"
    )

    inventory = get_repository_inventory(repo_path)

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "file_dataset.csv"
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "file_path",
            "language",
            "extension",
            "loc",
            "size_bytes"
        ])

        for root, directories, files in os.walk(repo_path):

            directories[:] = [
                d for d in directories
                if d != ".git"
            ]

            for filename in files:

                extension = os.path.splitext(filename)[1].lower()

                if extension not in [".py"]:
                    continue

                file_path = os.path.join(root, filename)

                relative_path = os.path.relpath(
                    file_path,
                    repo_path
                )

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as source_file:
                    loc = sum(1 for _ in source_file)

                size_bytes = os.path.getsize(file_path)

                writer.writerow([
                    relative_path,
                    "Python",
                    extension,
                    loc,
                    size_bytes
                ])

    print(f"Dataset generated: {output_path}")