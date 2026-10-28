"""Approach 1: deterministic lexical-feature hashing embeddings."""

from __future__ import annotations

import hashlib
import re

import numpy as np

from common import (
    DATA_DIR,
    normalize_rows,
    print_top_pairs,
    rank_pairs,
    read_selected_tokens,
    save_embeddings,
    save_pair_ranking,
)


DIMENSION = 64


def lexical_features(token: str) -> list[str]:
    """Describe spelling, subtoken structure and broad lexical shape."""

    bounded = f"<{token}>"
    features = [f"token={token}", f"length={min(len(token), 12)}"]
    features.extend(
        f"char{size}={bounded[start:start + size]}"
        for size in (2, 3, 4)
        for start in range(max(0, len(bounded) - size + 1))
    )

    subtokens = [part.lower() for part in re.findall(r"[A-Z]?[a-z]+|[A-Z]+|\d+", token)]
    features.extend(f"subtoken={part}" for part in subtokens)

    if token.isidentifier():
        features.append("shape=identifier")
    if token.isalpha():
        features.append("shape=alphabetic")
    if token.isdigit():
        features.append("shape=numeric")
    if token and all(not character.isalnum() for character in token):
        features.append("shape=punctuation")
    if "_" in token:
        features.append("shape=snake_case")
    return features


def embed_token(token: str, dimension: int = DIMENSION) -> np.ndarray:
    """Hash sparse lexical features into a fixed-width signed vector."""

    vector = np.zeros(dimension, dtype=np.float64)
    for feature in lexical_features(token):
        digest = hashlib.sha256(feature.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:8], "big") % dimension
        sign = 1.0 if digest[8] & 1 else -1.0
        vector[bucket] += sign
    return vector


def generate_embeddings(tokens: list[str], dimension: int = DIMENSION) -> np.ndarray:
    return normalize_rows(np.vstack([embed_token(token, dimension) for token in tokens]))


def main() -> None:
    tokens = read_selected_tokens()
    embeddings = generate_embeddings(tokens)
    pairs = rank_pairs(tokens, embeddings)

    save_embeddings(DATA_DIR / "feature_embeddings.csv", tokens, embeddings)
    save_pair_ranking(DATA_DIR / "feature_similarity.csv", pairs)
    print_top_pairs("Lexical-feature hashing", pairs)


if __name__ == "__main__":
    main()
