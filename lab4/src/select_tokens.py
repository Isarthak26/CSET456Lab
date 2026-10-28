"""Select 10 manual and 10 seeded-random tokens from the Lab 3 top 50."""

from __future__ import annotations

import csv
import random

from common import DATA_DIR


INPUT_FILE = DATA_DIR / "top_50_tokens.csv"
OUTPUT_FILE = DATA_DIR / "selected_20_tokens.csv"
RANDOM_SEED = 42

# These cover Python declarations, control flow, assertions, imports and values.
MANUAL_TOKENS = [
    "self",
    "def",
    "None",
    "is",
    "in",
    "assert",
    "for",
    "if",
    "import",
    "return",
]


def select_tokens() -> list[dict[str, str]]:
    with INPUT_FILE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_token = {row["token"]: row for row in rows}
    missing = [token for token in MANUAL_TOKENS if token not in by_token]
    if missing:
        raise ValueError(f"Manual tokens missing from top-50 file: {missing}")

    remaining = [row for row in rows if row["token"] not in MANUAL_TOKENS]
    random_rows = random.Random(RANDOM_SEED).sample(remaining, 10)

    selected: list[dict[str, str]] = []
    for token in MANUAL_TOKENS:
        selected.append({**by_token[token], "selection": "manual"})
    for row in random_rows:
        selected.append({**row, "selection": "seeded_random"})
    return selected


def main() -> None:
    selected = select_tokens()
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["token", "selection", "rank", "frequency"],
        )
        writer.writeheader()
        writer.writerows(selected)

    print(f"Saved {len(selected)} tokens to {OUTPUT_FILE}")
    for row in selected:
        print(f"{row['selection']:>13}: {row['token']!r}")


if __name__ == "__main__":
    main()
