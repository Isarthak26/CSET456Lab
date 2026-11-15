"""Small NumPy neural network used by the Lab 6 experiment."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np


Array = np.ndarray


def make_two_moons(samples: int = 1_200, noise: float = 0.16, seed: int = 42):
    """Create a balanced two-moons binary-classification data set."""
    if samples < 4:
        raise ValueError("samples must be at least 4")
    rng = np.random.default_rng(seed)
    first_count = samples // 2
    second_count = samples - first_count
    first_angle = rng.uniform(0.0, np.pi, first_count)
    second_angle = rng.uniform(0.0, np.pi, second_count)
    first = np.column_stack((np.cos(first_angle), np.sin(first_angle)))
    second = np.column_stack(
        (1.0 - np.cos(second_angle), 0.5 - np.sin(second_angle))
    )
    features = np.vstack((first, second))
    features += rng.normal(0.0, noise, features.shape)
    labels = np.concatenate((np.zeros(first_count), np.ones(second_count)))
    order = rng.permutation(samples)
    return features[order], labels[order, None]


def split_and_standardize(features: Array, labels: Array, seed: int = 42):
    """Return deterministic 70/15/15 train, validation and test splits."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(features))
    train_end = int(0.70 * len(features))
    validation_end = int(0.85 * len(features))
    train_ids = order[:train_end]
    validation_ids = order[train_end:validation_end]
    test_ids = order[validation_end:]
    mean = features[train_ids].mean(axis=0, keepdims=True)
    scale = features[train_ids].std(axis=0, keepdims=True)
    scale[scale == 0.0] = 1.0

    def subset(ids: Array):
        return (features[ids] - mean) / scale, labels[ids]

    return subset(train_ids), subset(validation_ids), subset(test_ids)


def binary_cross_entropy(probabilities: Array, labels: Array) -> float:
    probabilities = np.clip(probabilities, 1e-9, 1.0 - 1e-9)
    return float(
        -np.mean(labels * np.log(probabilities) + (1.0 - labels) * np.log(1.0 - probabilities))
    )


def accuracy(probabilities: Array, labels: Array) -> float:
    return float(np.mean((probabilities >= 0.5) == labels))


@dataclass
class TrainingResult:
    history: list[dict[str, float | int]]
    target_epoch: int | None
    target_seconds: float | None
    training_seconds: float


class NeuralNetwork:
    """Fully connected ReLU network with a sigmoid output and Adam training."""

    def __init__(self, input_size: int, hidden_sizes: list[int], seed: int = 42):
        if not hidden_sizes or any(size <= 0 for size in hidden_sizes):
            raise ValueError("hidden_sizes must contain positive integers")
        self.hidden_sizes = list(hidden_sizes)
        rng = np.random.default_rng(seed)
        sizes = [input_size, *hidden_sizes, 1]
        self.weights = []
        self.biases = []
        for input_width, output_width in zip(sizes[:-1], sizes[1:]):
            self.weights.append(
                rng.normal(0.0, np.sqrt(2.0 / input_width), (input_width, output_width))
            )
            self.biases.append(np.zeros((1, output_width)))

    @property
    def parameter_count(self) -> int:
        return sum(value.size for value in [*self.weights, *self.biases])

    def forward(self, features: Array):
        activations = [features]
        pre_activations = []
        current = features
        for weights, bias in zip(self.weights[:-1], self.biases[:-1]):
            before_relu = current @ weights + bias
            pre_activations.append(before_relu)
            current = np.maximum(before_relu, 0.0)
            activations.append(current)
        logits = current @ self.weights[-1] + self.biases[-1]
        probabilities = np.empty_like(logits)
        positive = logits >= 0
        probabilities[positive] = 1.0 / (1.0 + np.exp(-logits[positive]))
        exponential = np.exp(logits[~positive])
        probabilities[~positive] = exponential / (1.0 + exponential)
        return probabilities, activations, pre_activations

    def predict(self, features: Array) -> Array:
        return self.forward(features)[0]

    def gradients(self, features: Array, labels: Array):
        probabilities, activations, pre_activations = self.forward(features)
        weight_gradients = [np.empty_like(value) for value in self.weights]
        bias_gradients = [np.empty_like(value) for value in self.biases]
        delta = (probabilities - labels) / len(features)
        weight_gradients[-1] = activations[-1].T @ delta
        bias_gradients[-1] = delta.sum(axis=0, keepdims=True)
        for layer in range(len(self.weights) - 2, -1, -1):
            delta = (delta @ self.weights[layer + 1].T) * (pre_activations[layer] > 0.0)
            weight_gradients[layer] = activations[layer].T @ delta
            bias_gradients[layer] = delta.sum(axis=0, keepdims=True)
        return weight_gradients, bias_gradients

    def fit(
        self,
        train_features: Array,
        train_labels: Array,
        validation_features: Array,
        validation_labels: Array,
        *,
        epochs: int = 400,
        batch_size: int = 64,
        learning_rate: float = 0.01,
        target_accuracy: float = 0.90,
        seed: int = 42,
    ) -> TrainingResult:
        rng = np.random.default_rng(seed)
        parameters = [*self.weights, *self.biases]
        first_moments = [np.zeros_like(value) for value in parameters]
        second_moments = [np.zeros_like(value) for value in parameters]
        beta_1, beta_2 = 0.9, 0.999
        step = 0
        history = []
        target_epoch = None
        target_seconds = None
        started = perf_counter()

        for epoch in range(1, epochs + 1):
            order = rng.permutation(len(train_features))
            for start in range(0, len(order), batch_size):
                batch_ids = order[start : start + batch_size]
                weight_gradients, bias_gradients = self.gradients(
                    train_features[batch_ids], train_labels[batch_ids]
                )
                gradients = [*weight_gradients, *bias_gradients]
                step += 1
                for index, (parameter, gradient) in enumerate(zip(parameters, gradients)):
                    first_moments[index] = beta_1 * first_moments[index] + (1.0 - beta_1) * gradient
                    second_moments[index] = beta_2 * second_moments[index] + (1.0 - beta_2) * gradient**2
                    first_hat = first_moments[index] / (1.0 - beta_1**step)
                    second_hat = second_moments[index] / (1.0 - beta_2**step)
                    parameter -= learning_rate * first_hat / (np.sqrt(second_hat) + 1e-8)

            train_probabilities = self.predict(train_features)
            validation_probabilities = self.predict(validation_features)
            validation_accuracy = accuracy(validation_probabilities, validation_labels)
            elapsed = perf_counter() - started
            history.append(
                {
                    "epoch": epoch,
                    "train_loss": binary_cross_entropy(train_probabilities, train_labels),
                    "train_accuracy": accuracy(train_probabilities, train_labels),
                    "validation_loss": binary_cross_entropy(
                        validation_probabilities, validation_labels
                    ),
                    "validation_accuracy": validation_accuracy,
                    "elapsed_seconds": elapsed,
                }
            )
            if target_epoch is None and validation_accuracy >= target_accuracy:
                target_epoch = epoch
                target_seconds = elapsed

        return TrainingResult(history, target_epoch, target_seconds, perf_counter() - started)


def gradient_check(
    network: NeuralNetwork,
    features: Array,
    labels: Array,
    epsilon: float = 1e-5,
) -> float:
    """Compare every analytic gradient with a finite-difference estimate."""
    analytic_weights, analytic_biases = network.gradients(features, labels)
    maximum_relative_error = 0.0
    for parameter, analytic in zip(
        [*network.weights, *network.biases], [*analytic_weights, *analytic_biases]
    ):
        for index in np.ndindex(parameter.shape):
            original = parameter[index]
            parameter[index] = original + epsilon
            positive_loss = binary_cross_entropy(network.predict(features), labels)
            parameter[index] = original - epsilon
            negative_loss = binary_cross_entropy(network.predict(features), labels)
            parameter[index] = original
            numeric = (positive_loss - negative_loss) / (2.0 * epsilon)
            relative_error = abs(numeric - analytic[index]) / max(
                1e-8, abs(numeric) + abs(analytic[index])
            )
            maximum_relative_error = max(maximum_relative_error, relative_error)
    return maximum_relative_error
