"""Approach 2: repository co-occurrence embeddings using PPMI and SVD."""

from __future__ import annotations

from collections import Counter

import numpy as np

from common import (
    DATA_DIR,
    load_token_sequences,
    normalize_rows,
    print_top_pairs,
    rank_pairs,
    read_selected_tokens,
    save_embeddings,
    save_pair_ranking,
)


VOCAB_SIZE = 300
WINDOW_SIZE = 4
EMBEDDING_DIMENSION = 32


def build_cooccurrence_matrix(
    sequences: list[list[str]],
    selected_tokens: list[str],
    *,
    vocab_size: int = VOCAB_SIZE,
    window_size: int = WINDOW_SIZE,
) -> tuple[list[str], np.ndarray]:
    frequencies = Counter(token for sequence in sequences for token in sequence)
    vocabulary = [token for token, _ in frequencies.most_common(vocab_size)]
    for token in selected_tokens:
        if token not in vocabulary:
            vocabulary.append(token)

    token_to_index = {token: index for index, token in enumerate(vocabulary)}
    matrix = np.zeros((len(vocabulary), len(vocabulary)), dtype=np.float64)

    for sequence in sequences:
        for position, token in enumerate(sequence):
            center = token_to_index.get(token)
            if center is None:
                continue
            start = max(0, position - window_size)
            stop = min(len(sequence), position + window_size + 1)
            for context_position in range(start, stop):
                if context_position == position:
                    continue
                context = token_to_index.get(sequence[context_position])
                if context is not None:
                    distance = abs(position - context_position)
                    matrix[center, context] += 1.0 / distance
    return vocabulary, matrix


def ppmi_svd_embeddings(
    cooccurrence: np.ndarray,
    dimension: int = EMBEDDING_DIMENSION,
) -> np.ndarray:
    total = float(cooccurrence.sum())
    row_totals = cooccurrence.sum(axis=1, keepdims=True)
    column_totals = cooccurrence.sum(axis=0, keepdims=True)
    expected = row_totals @ column_totals

    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((cooccurrence * total) / np.maximum(expected, 1e-12))
    ppmi = np.maximum(np.nan_to_num(pmi, nan=0.0, neginf=0.0, posinf=0.0), 0.0)

    left, singular_values, _ = np.linalg.svd(ppmi, full_matrices=False)
    width = min(dimension, len(singular_values))
    embeddings = left[:, :width] * np.sqrt(singular_values[:width])
    return normalize_rows(embeddings)


def main() -> None:
    selected_tokens = read_selected_tokens()
    sequences, token_count = load_token_sequences()
    vocabulary, cooccurrence = build_cooccurrence_matrix(sequences, selected_tokens)
    all_embeddings = ppmi_svd_embeddings(cooccurrence)

    vocabulary_index = {token: index for index, token in enumerate(vocabulary)}
    selected_embeddings = np.vstack(
        [all_embeddings[vocabulary_index[token]] for token in selected_tokens]
    )
    pairs = rank_pairs(selected_tokens, selected_embeddings)

    save_embeddings(DATA_DIR / "cooccurrence_embeddings.csv", selected_tokens, selected_embeddings)
    save_pair_ranking(DATA_DIR / "cooccurrence_similarity.csv", pairs)
    print(f"Processed {token_count:,} BPE tokens in {len(sequences):,} files.")
    print_top_pairs("PPMI-SVD co-occurrence", pairs)


if __name__ == "__main__":
    main()
