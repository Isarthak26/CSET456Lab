"""Shared utilities for the Lab 4 embedding experiments."""

from __future__ import annotations

import csv
import math
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

import numpy as np


LAB_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_DIR.parent
DATA_DIR = LAB_DIR / "data"
OUTPUT_DIR = LAB_DIR / "output"

SOURCE_DATASET = REPO_ROOT / "lab3" / "data" / "all_repositories.csv"
TOKENIZER_FILE = REPO_ROOT / "lab3" / "output" / "subword_tokenizer.json"
SELECTED_TOKENS_FILE = DATA_DIR / "selected_20_tokens.csv"


def set_csv_field_limit() -> None:
    """Allow the CSV module to read large source-code fields."""

    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10


def read_selected_tokens(path: Path = SELECTED_TOKENS_FILE) -> list[str]:
    """Read the 20 experiment tokens in their recorded selection order."""

    with path.open(encoding="utf-8", newline="") as handle:
        tokens = [row["token"] for row in csv.DictReader(handle)]

    if len(tokens) != 20 or len(set(tokens)) != 20:
        raise ValueError(
            f"Expected 20 unique tokens in {path}, found {len(tokens)} rows."
        )
    return tokens


def iter_source_rows(
    dataset_path: Path = SOURCE_DATASET,
    *,
    max_files: int | None = None,
    python_only: bool = False,
) -> Iterator[dict[str, str]]:
    """Yield source-code dataset rows without loading the 25 MB CSV at once."""

    set_csv_field_limit()
    yielded = 0
    with dataset_path.open(encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"source_code", "file_path", "file_extension", "repository"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing dataset columns: {sorted(missing)}")

        for row in reader:
            source = row.get("source_code", "")
            extension = row.get("file_extension", "").lower()
            if not source or (python_only and extension not in {".py", "py"}):
                continue
            yield row
            yielded += 1
            if max_files is not None and yielded >= max_files:
                return


def load_tokenizer():
    """Load the BPE tokenizer trained in Lab 3 (imported lazily for tests)."""

    try:
        from tokenizers import Tokenizer
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "The 'tokenizers' package is required. Install lab4/requirements.txt."
        ) from exc

    if not TOKENIZER_FILE.exists():
        raise FileNotFoundError(
            f"Lab 3 tokenizer not found at {TOKENIZER_FILE}. Run Lab 3 first."
        )
    return Tokenizer.from_file(str(TOKENIZER_FILE))


def load_token_sequences(
    *,
    max_files: int = 1_500,
    max_tokens: int = 1_000_000,
) -> tuple[list[list[str]], int]:
    """Tokenize the Lab 3 corpus while retaining file boundaries."""

    tokenizer = load_tokenizer()
    sequences: list[list[str]] = []
    token_count = 0

    for row in iter_source_rows(max_files=max_files):
        remaining = max_tokens - token_count
        if remaining <= 0:
            break
        tokens = tokenizer.encode(row["source_code"]).tokens[:remaining]
        if tokens:
            sequences.append(tokens)
            token_count += len(tokens)

    if not sequences:
        raise ValueError("No token sequences were produced from the Lab 3 dataset.")
    return sequences, token_count


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    """Return an L2-normalized copy of a two-dimensional matrix."""

    matrix = np.asarray(matrix, dtype=np.float64)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-12)


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Compute cosine similarity, returning 0 for a zero vector."""

    denominator = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(vector_a, vector_b) / denominator)


def rank_pairs(
    labels: Sequence[str], matrix: np.ndarray
) -> list[tuple[str, str, float]]:
    """Rank every unique label pair by descending cosine similarity."""

    if len(labels) != len(matrix):
        raise ValueError("Number of labels and embedding rows must match.")

    normalized = normalize_rows(matrix)
    results: list[tuple[str, str, float]] = []
    for left in range(len(labels)):
        for right in range(left + 1, len(labels)):
            similarity = float(np.dot(normalized[left], normalized[right]))
            if not math.isfinite(similarity):
                similarity = 0.0
            results.append((labels[left], labels[right], similarity))
    return sorted(results, key=lambda item: item[2], reverse=True)


def save_embeddings(path: Path, labels: Sequence[str], matrix: np.ndarray) -> None:
    """Save embeddings in a readable CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["token", *[f"dim_{index:02d}" for index in range(matrix.shape[1])]])
        for label, vector in zip(labels, matrix, strict=True):
            writer.writerow([label, *[f"{float(value):.8f}" for value in vector]])


def save_pair_ranking(
    path: Path, pairs: Sequence[tuple[str, str, float]]
) -> None:
    """Save a complete pairwise similarity ranking."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "token_1", "token_2", "cosine_similarity"])
        for rank, (left, right, similarity) in enumerate(pairs, start=1):
            writer.writerow([rank, left, right, f"{similarity:.8f}"])


def print_top_pairs(name: str, pairs: Sequence[tuple[str, str, float]]) -> None:
    """Print the five most similar pairs for a reproducible run log."""

    print(f"\n{name} - top 5 most similar pairs")
    for rank, (left, right, similarity) in enumerate(pairs[:5], start=1):
        print(f"{rank}. {left!r} <-> {right!r}: {similarity:.6f}")
