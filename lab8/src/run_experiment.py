"""Fine-tune BERT-tiny and compare it with the Lab 7 LSTM."""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer


LAB_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = LAB_DIR.parent
LAB7_SRC = REPOSITORY_DIR / "lab7" / "src"
sys.path.insert(0, str(LAB7_SRC))

from data_utils import load_sms_data, stratified_split  # noqa: E402
from transformer_model import (  # noqa: E402
    TransformerSmsDataset,
    build_comparison,
    evaluate,
    train_model,
)


OUTPUT_DIR = LAB_DIR / "output"
MODEL_NAME = "prajjwal1/bert-tiny"
SEED = 42


def select(values, indices):
    return [values[index] for index in indices]


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    texts, labels = load_sms_data(download=False)
    splits = stratified_split(labels, seed=SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    datasets = {}
    for name, indices in splits.items():
        datasets[name] = TransformerSmsDataset(
            select(texts, indices),
            labels[indices],
            tokenizer,
            maximum_length=80,
        )
    generator = torch.Generator().manual_seed(SEED)
    train_loader = DataLoader(
        datasets["train"], batch_size=32, shuffle=True, generator=generator
    )
    validation_loader = DataLoader(datasets["validation"], batch_size=64)
    test_loader = DataLoader(datasets["test"], batch_size=64)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2
    )
    history, training_seconds, loss_function = train_model(
        model,
        train_loader,
        validation_loader,
        epochs=4,
        learning_rate=5e-5,
        device=device,
    )
    test_metrics = evaluate(model, test_loader, loss_function, device)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    result = {
        "model": "BERT-tiny transformer",
        "pretrained_checkpoint": MODEL_NAME,
        "task": "UCI SMS spam classification",
        "seed": SEED,
        "device": str(device),
        "train_samples": len(datasets["train"]),
        "validation_samples": len(datasets["validation"]),
        "test_samples": len(datasets["test"]),
        "wordpiece_vocabulary_size": tokenizer.vocab_size,
        "maximum_sequence_length": 80,
        "parameter_count": parameter_count,
        "training_seconds": training_seconds,
        **{f"test_{key}": value for key, value in test_metrics.items()},
    }

    with (REPOSITORY_DIR / "lab7" / "output" / "metrics.json").open(
        encoding="utf-8"
    ) as input_file:
        lstm_metrics = json.load(input_file)
    comparison_rows, comparison_summary = build_comparison(lstm_metrics, result)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / "metrics.json").open("w", encoding="utf-8") as output_file:
        json.dump(result, output_file, indent=2)
    with (OUTPUT_DIR / "comparison_summary.json").open(
        "w", encoding="utf-8"
    ) as output_file:
        json.dump(comparison_summary, output_file, indent=2)
    with (OUTPUT_DIR / "model_comparison.csv").open(
        "w", encoding="utf-8", newline=""
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(comparison_rows[0]))
        writer.writeheader()
        writer.writerows(comparison_rows)
    with (OUTPUT_DIR / "training_history.csv").open(
        "w", encoding="utf-8", newline=""
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)

    print("\nLab 8 transformer test result")
    print(json.dumps(result, indent=2))
    print("\nTransformer versus LSTM")
    print(json.dumps(comparison_summary, indent=2))


if __name__ == "__main__":
    main()
