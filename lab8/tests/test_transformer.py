"""Tests that do not require downloading the pretrained checkpoint."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = LAB_DIR.parent
sys.path.insert(0, str(REPOSITORY_DIR / "lab7" / "src"))
sys.path.insert(0, str(LAB_DIR / "src"))

from data_utils import load_sms_data, stratified_split  # noqa: E402
from transformer_model import build_comparison  # noqa: E402


class SharedExperimentTests(unittest.TestCase):
    def test_lab8_uses_same_seeded_split_sizes_as_lab7(self):
        _, labels = load_sms_data(download=False)
        splits = stratified_split(labels, seed=42)
        self.assertEqual(
            {name: len(ids) for name, ids in splits.items()},
            {"train": 3900, "validation": 836, "test": 838},
        )

    def test_recorded_lab7_counts_match_shared_split(self):
        with (REPOSITORY_DIR / "lab7" / "output" / "metrics.json").open() as file:
            metrics = json.load(file)
        self.assertEqual(metrics["train_samples"], 3900)
        self.assertEqual(metrics["validation_samples"], 836)
        self.assertEqual(metrics["test_samples"], 838)


class ComparisonTests(unittest.TestCase):
    def test_comparison_calculates_ratios_and_differences(self):
        base = {
            "test_accuracy": 0.90,
            "test_precision": 0.90,
            "test_recall": 0.80,
            "test_f1": 0.85,
            "parameter_count": 100,
            "training_seconds": 2.0,
            "test_milliseconds_per_message": 0.5,
        }
        lstm = {"model": "LSTM", **base}
        transformer = {
            "model": "Transformer",
            **base,
            "test_accuracy": 0.95,
            "test_f1": 0.90,
            "parameter_count": 500,
            "training_seconds": 8.0,
            "test_milliseconds_per_message": 1.0,
        }
        rows, summary = build_comparison(lstm, transformer)
        self.assertEqual(len(rows), 2)
        self.assertEqual(summary["transformer_to_lstm_parameter_ratio"], 5.0)
        self.assertEqual(summary["transformer_to_lstm_training_time_ratio"], 4.0)
        self.assertAlmostEqual(summary["transformer_minus_lstm_accuracy"], 0.05)
        self.assertAlmostEqual(summary["transformer_minus_lstm_f1"], 0.05)


if __name__ == "__main__":
    unittest.main()
