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


if __name__ == "__main__":
    unittest.main()
