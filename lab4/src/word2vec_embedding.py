"""A compact NumPy implementation of skip-gram Word2Vec with negative sampling."""

from __future__ import annotations

import csv
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


RANDOM_SEED = 42
VOCAB_SIZE = 300
WINDOW_SIZE = 3
EMBEDDING_DIMENSION = 48
NEGATIVE_SAMPLES = 5
MAX_PAIRS = 300_000
EPOCHS = 3
BATCH_SIZE = 512
INITIAL_LEARNING_RATE = 0.025


def build_vocabulary(
    sequences: list[list[str]],
    required_tokens: list[str],
    vocab_size: int = VOCAB_SIZE,
) -> tuple[list[str], np.ndarray]:
    frequencies = Counter(token for sequence in sequences for token in sequence)
    vocabulary = [token for token, _ in frequencies.most_common(vocab_size)]
    for token in required_tokens:
        if token not in vocabulary:
            vocabulary.append(token)
    counts = np.array([frequencies.get(token, 1) for token in vocabulary], dtype=np.float64)
    return vocabulary, counts


def make_skipgram_pairs(
    sequences: list[list[str]],
    token_to_index: dict[str, int],
    *,
    window_size: int = WINDOW_SIZE,
    max_pairs: int = MAX_PAIRS,
) -> tuple[np.ndarray, np.ndarray]:
    """Create positive center-context examples without crossing file boundaries."""

    centers: list[int] = []
    contexts: list[int] = []
    for sequence in sequences:
        ids = [token_to_index.get(token, -1) for token in sequence]
        for position, center in enumerate(ids):
            if center < 0:
                continue
            start = max(0, position - window_size)
            stop = min(len(ids), position + window_size + 1)
            for context_position in range(start, stop):
                context = ids[context_position]
                if context_position != position and context >= 0:
                    centers.append(center)
                    contexts.append(context)
                    if len(centers) >= max_pairs:
                        return np.asarray(centers), np.asarray(contexts)
    return np.asarray(centers), np.asarray(contexts)


def _sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -15.0, 15.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def train_skipgram_negative_sampling(
    centers: np.ndarray,
    contexts: np.ndarray,
    frequencies: np.ndarray,
    *,
    dimension: int = EMBEDDING_DIMENSION,
    negative_samples: int = NEGATIVE_SAMPLES,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = INITIAL_LEARNING_RATE,
    seed: int = RANDOM_SEED,
) -> tuple[np.ndarray, list[float]]:
    """Train SGNS and return input embeddings plus mean loss per epoch."""

    if len(centers) == 0:
        raise ValueError("At least one skip-gram pair is required.")

    rng = np.random.default_rng(seed)
    vocabulary_size = len(frequencies)
    bound = 0.5 / dimension
    input_embeddings = rng.uniform(
        -bound, bound, size=(vocabulary_size, dimension)
    ).astype(np.float64)
    output_embeddings = np.zeros((vocabulary_size, dimension), dtype=np.float64)

    negative_distribution = np.power(np.maximum(frequencies, 1.0), 0.75)
    negative_distribution /= negative_distribution.sum()
    order = np.arange(len(centers))
    epoch_losses: list[float] = []

    for epoch in range(epochs):
        rng.shuffle(order)
        total_loss = 0.0
        examples = 0
        progress = epoch / max(epochs, 1)
        current_rate = learning_rate * max(0.2, 1.0 - 0.8 * progress)

        for start in range(0, len(order), batch_size):
            batch_indices = order[start : start + batch_size]
            center_ids = centers[batch_indices]
            positive_ids = contexts[batch_indices]
            batch_length = len(batch_indices)
            negative_ids = rng.choice(
                vocabulary_size,
                size=(batch_length, negative_samples),
                p=negative_distribution,
            )

            center_vectors = input_embeddings[center_ids].copy()
            positive_vectors = output_embeddings[positive_ids].copy()
            negative_vectors = output_embeddings[negative_ids].copy()

            positive_scores = np.sum(center_vectors * positive_vectors, axis=1)
            negative_scores = np.einsum("bd,bkd->bk", center_vectors, negative_vectors)
            positive_probabilities = _sigmoid(positive_scores)
            negative_probabilities = _sigmoid(negative_scores)

            total_loss += float(
                -np.log(positive_probabilities + 1e-12).sum()
                - np.log(1.0 - negative_probabilities + 1e-12).sum()
            )
            examples += batch_length

            positive_error = positive_probabilities - 1.0
            negative_error = negative_probabilities
            center_gradient = (
                positive_error[:, None] * positive_vectors
                + np.einsum("bk,bkd->bd", negative_error, negative_vectors)
            )
            positive_gradient = positive_error[:, None] * center_vectors
            negative_gradient = negative_error[:, :, None] * center_vectors[:, None, :]

            np.add.at(
                input_embeddings,
                center_ids,
                -current_rate * np.clip(center_gradient, -2.0, 2.0),
            )
            np.add.at(
                output_embeddings,
                positive_ids,
                -current_rate * np.clip(positive_gradient, -2.0, 2.0),
            )
            np.add.at(
                output_embeddings,
                negative_ids.reshape(-1),
                -current_rate * np.clip(negative_gradient, -2.0, 2.0).reshape(
                    -1, dimension
                ),
            )

        epoch_losses.append(total_loss / max(examples, 1))
        print(f"Word2Vec epoch {epoch + 1}/{epochs}: mean loss={epoch_losses[-1]:.6f}")

    return normalize_rows(input_embeddings), epoch_losses


def main() -> None:
    selected_tokens = read_selected_tokens()
    sequences, token_count = load_token_sequences(max_tokens=750_000)
    vocabulary, frequencies = build_vocabulary(sequences, selected_tokens)
    token_to_index = {token: index for index, token in enumerate(vocabulary)}
    centers, contexts = make_skipgram_pairs(sequences, token_to_index)

    all_embeddings, losses = train_skipgram_negative_sampling(
        centers, contexts, frequencies
    )
    selected_embeddings = np.vstack(
        [all_embeddings[token_to_index[token]] for token in selected_tokens]
    )
    pairs = rank_pairs(selected_tokens, selected_embeddings)

    save_embeddings(DATA_DIR / "word2vec_embeddings.csv", selected_tokens, selected_embeddings)
    save_pair_ranking(DATA_DIR / "word2vec_similarity.csv", pairs)
    with (DATA_DIR / "word2vec_training.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["epoch", "mean_negative_sampling_loss"])
        writer.writerows((index, f"{loss:.8f}") for index, loss in enumerate(losses, 1))

    print(
        f"Trained on {len(centers):,} positive pairs from "
        f"{token_count:,} tokens; vocabulary={len(vocabulary)}."
    )
    print_top_pairs("Word2Vec SGNS", pairs)


if __name__ == "__main__":
    main()
