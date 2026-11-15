"""Run the Lab 6 architecture comparison and save reproducible results."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from neural_network import (
    NeuralNetwork,
    accuracy,
    binary_cross_entropy,
    gradient_check,
    make_two_moons,
    split_and_standardize,
)


LAB_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = LAB_DIR / "output"
TARGET_ACCURACY = 0.90


def write_csv(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    features, labels = make_two_moons()
    train, validation, test = split_and_standardize(features, labels)

    checker = NeuralNetwork(2, [3], seed=7)
    check_features = np.array([[0.2, -0.4], [0.7, 0.1], [-0.3, 0.8]])
    check_labels = np.array([[0.0], [1.0], [0.0]])
    maximum_gradient_error = gradient_check(checker, check_features, check_labels)
    if maximum_gradient_error >= 1e-5:
        raise AssertionError(f"gradient check failed: {maximum_gradient_error:.3e}")

    configurations = {
        "single_hidden_layer": [30],
        "three_hidden_layers": [10, 10, 10],
    }
    summaries = []
    for name, hidden_sizes in configurations.items():
        model = NeuralNetwork(2, hidden_sizes, seed=42)
        result = model.fit(
            *train,
            *validation,
            epochs=300,
            target_accuracy=TARGET_ACCURACY,
        )
        test_probabilities = model.predict(test[0])
        summaries.append(
            {
                "architecture": name,
                "hidden_layers": "-".join(map(str, hidden_sizes)),
                "total_hidden_nodes": sum(hidden_sizes),
                "parameters": model.parameter_count,
                "target_validation_accuracy": TARGET_ACCURACY,
                "epoch_to_target": result.target_epoch or "not_reached",
                "seconds_to_target": (
                    f"{result.target_seconds:.6f}"
                    if result.target_seconds is not None
                    else "not_reached"
                ),
                "training_seconds": f"{result.training_seconds:.6f}",
                "final_validation_accuracy": f"{result.history[-1]['validation_accuracy']:.6f}",
                "test_loss": f"{binary_cross_entropy(test_probabilities, test[1]):.6f}",
                "test_accuracy": f"{accuracy(test_probabilities, test[1]):.6f}",
                "gradient_check_max_relative_error": f"{maximum_gradient_error:.3e}",
            }
        )
        write_csv(OUTPUT_DIR / f"{name}_history.csv", result.history)

    write_csv(OUTPUT_DIR / "architecture_comparison.csv", summaries)
    print("Lab 6: same hidden-node budget, different depth")
    print(f"Gradient check maximum relative error: {maximum_gradient_error:.3e}")
    for row in summaries:
        print(
            f"{row['architecture']}: {row['hidden_layers']} hidden nodes, "
            f"{row['parameters']} parameters, target at epoch {row['epoch_to_target']} "
            f"({row['seconds_to_target']} s), test accuracy {row['test_accuracy']}"
        )


if __name__ == "__main__":
    main()
