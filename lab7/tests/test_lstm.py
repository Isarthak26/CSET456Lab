"""Small correctness tests for Lab 7."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import torch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_utils import (  # noqa: E402
    build_vocabulary,
    classification_metrics,
    encode_text,
    stratified_split,
)
from lstm_model import LstmClassifier  # noqa: E402


class DataTests(unittest.TestCase):
    def test_stratified_splits_are_disjoint_and_complete(self):
        labels = np.array([0] * 80 + [1] * 20)
        splits = stratified_split(labels, seed=3)
        combined = np.concatenate(list(splits.values()))
        self.assertEqual(len(np.unique(combined)), len(labels))
        self.assertEqual(set(combined), set(range(len(labels))))
        for ids in splits.values():
            self.assertAlmostEqual(labels[ids].mean(), 0.20, delta=0.02)

    def test_vocabulary_uses_only_frequent_tokens_and_encodes_unknown(self):
        vocabulary = build_vocabulary(["hello student", "hello lab"], min_frequency=2)
        self.assertIn("hello", vocabulary)
        self.assertNotIn("student", vocabulary)
        token_ids, length = encode_text("hello mystery", vocabulary, maximum_length=4)
        self.assertEqual(length, 2)
        self.assertEqual(token_ids, [vocabulary["hello"], 1, 0, 0])

    def test_metric_values(self):
        metrics = classification_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertEqual(metrics["precision"], 0.5)
        self.assertEqual(metrics["recall"], 0.5)
        self.assertEqual(metrics["f1"], 0.5)


class ModelTests(unittest.TestCase):
    def test_lstm_returns_one_logit_per_message(self):
        model = LstmClassifier(vocabulary_size=20, embedding_size=8, hidden_size=6)
        token_ids = torch.tensor([[2, 3, 0], [4, 5, 6]])
        lengths = torch.tensor([2, 3])
        self.assertEqual(tuple(model(token_ids, lengths).shape), (2,))


if __name__ == "__main__":
    unittest.main()
