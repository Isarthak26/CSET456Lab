"""Small deterministic tests for the two original Lab 4 approaches."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from common import cosine_similarity, rank_pairs  # noqa: E402
from cooccurrence_embedding import ppmi_svd_embeddings  # noqa: E402
from feature_embedding import embed_token, generate_embeddings  # noqa: E402
from select_tokens import select_tokens  # noqa: E402
from word2vec_embedding import (  # noqa: E402
    build_vocabulary,
    make_skipgram_pairs,
    train_skipgram_negative_sampling,
)
from code2vec_embedding import (  # noqa: E402
    extract_functions_from_source,
    pool_function_embeddings,
    train_code2vec,
    vectorize_examples,
)


class TokenSelectionTests(unittest.TestCase):
    def test_selection_is_balanced_and_unique(self) -> None:
        rows = select_tokens()
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({row["token"] for row in rows}), 20)
        self.assertEqual(sum(row["selection"] == "manual" for row in rows), 10)
        self.assertEqual(sum(row["selection"] == "seeded_random" for row in rows), 10)


class FeatureEmbeddingTests(unittest.TestCase):
    def test_hashing_is_deterministic(self) -> None:
        np.testing.assert_array_equal(embed_token("import"), embed_token("import"))

    def test_generated_rows_are_normalized(self) -> None:
        matrix = generate_embeddings(["import", "return", "=="])
        np.testing.assert_allclose(np.linalg.norm(matrix, axis=1), np.ones(3))


class SimilarityTests(unittest.TestCase):
    def test_cosine_handles_zero_vector(self) -> None:
        self.assertEqual(cosine_similarity(np.zeros(2), np.ones(2)), 0.0)

    def test_pair_ranking_has_n_choose_two_rows(self) -> None:
        matrix = np.eye(4)
        self.assertEqual(len(rank_pairs(["a", "b", "c", "d"], matrix)), 6)

    def test_ppmi_svd_returns_finite_vectors(self) -> None:
        counts = np.array(
            [
                [0.0, 4.0, 1.0],
                [4.0, 0.0, 2.0],
                [1.0, 2.0, 0.0],
            ]
        )
        embeddings = ppmi_svd_embeddings(counts, dimension=2)
        self.assertEqual(embeddings.shape, (3, 2))
        self.assertTrue(np.isfinite(embeddings).all())


class Word2VecTests(unittest.TestCase):
    def test_tiny_skipgram_training(self) -> None:
        sequences = [["for", "item", "in", "items"]] * 8
        vocabulary, frequencies = build_vocabulary(
            sequences, ["for", "in"], vocab_size=4
        )
        token_to_index = {token: index for index, token in enumerate(vocabulary)}
        centers, contexts = make_skipgram_pairs(
            sequences, token_to_index, window_size=1, max_pairs=100
        )
        embeddings, losses = train_skipgram_negative_sampling(
            centers,
            contexts,
            frequencies,
            dimension=8,
            negative_samples=2,
            epochs=1,
            batch_size=16,
        )
        self.assertEqual(embeddings.shape, (4, 8))
        self.assertEqual(len(losses), 1)
        self.assertTrue(np.isfinite(embeddings).all())


class Code2VecTests(unittest.TestCase):
    def test_extract_train_and_pool_tiny_program(self) -> None:
        source = """
def add(left, right):
    return left + right

def multiply(left, right):
    result = left * right
    return result
"""
        examples = extract_functions_from_source("demo", "maths.py", source)
        self.assertEqual([example.method_name for example in examples], ["add", "multiply"])
        metadata, starts, paths, ends, targets, functions = vectorize_examples(examples)
        terminal_embeddings, path_embeddings, _, losses = train_code2vec(
            starts,
            paths,
            ends,
            targets,
            terminal_count=len(metadata["terminal_vocab"]),
            path_count=len(metadata["path_vocab"]),
            target_count=len(metadata["target_vocab"]),
            dimension=8,
            negative_samples=2,
            epochs=1,
            batch_size=16,
        )
        pooled = pool_function_embeddings(
            starts,
            paths,
            ends,
            functions,
            terminal_embeddings,
            path_embeddings,
            len(examples),
        )
        self.assertEqual(pooled.shape, (2, 8))
        self.assertEqual(len(losses), 1)
        self.assertTrue(np.isfinite(pooled).all())


if __name__ == "__main__":
    unittest.main()
