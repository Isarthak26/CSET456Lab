import json
import os

from repository_inventory import get_repository_inventory
from git_history import get_git_history


if __name__ == "__main__":

    repo_path = os.path.expanduser(
        "~/repository_mining/requests"
    )

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "output"
    )

    os.makedirs(output_dir, exist_ok=True)

    inventory = get_repository_inventory(repo_path)
    history = get_git_history(repo_path)

    inventory.pop("dataset_rows", None)

    stats = {
        "repository_inventory": inventory,
        "git_history": history
    }

    output_path = os.path.join(
        output_dir,
        "repository_stats.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            stats,
            file,
            indent=4
        )

    print(f"JSON statistics generated: {output_path}")
