"""Correctness tests for the Lab 6 neural network."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from neural_network import (  # noqa: E402
    NeuralNetwork,
    accuracy,
    gradient_check,
    make_two_moons,
    split_and_standardize,
)


class NeuralNetworkTests(unittest.TestCase):
    def test_architectures_have_same_hidden_node_budget(self):
        self.assertEqual(sum([30]), sum([10, 10, 10]))

    def test_forward_shape_and_probability_range(self):
        model = NeuralNetwork(2, [5, 4], seed=1)
        predictions = model.predict(np.ones((7, 2)))
        self.assertEqual(predictions.shape, (7, 1))
        self.assertTrue(np.all((predictions >= 0.0) & (predictions <= 1.0)))

    def test_backpropagation_passes_numerical_gradient_check(self):
        model = NeuralNetwork(2, [3], seed=7)
        features = np.array([[0.2, -0.4], [0.7, 0.1], [-0.3, 0.8]])
        labels = np.array([[0.0], [1.0], [0.0]])
        self.assertLess(gradient_check(model, features, labels), 1e-5)

    def test_network_learns_better_than_chance(self):
        features, labels = make_two_moons(samples=400, seed=11)
        train, validation, _ = split_and_standardize(features, labels, seed=11)
        model = NeuralNetwork(2, [10], seed=11)
        model.fit(*train, *validation, epochs=80, seed=11)
        self.assertGreater(accuracy(model.predict(validation[0]), validation[1]), 0.85)


if __name__ == "__main__":
    unittest.main()
