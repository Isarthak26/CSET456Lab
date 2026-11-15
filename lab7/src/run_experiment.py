"""Train and evaluate an LSTM on the UCI SMS Spam Collection."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from data_utils import build_vocabulary, load_sms_data, stratified_split
from lstm_model import LstmClassifier, SmsDataset, evaluate, train_model


LAB_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = LAB_DIR / "output"
SEED = 42


def select(values, indices):
    return [values[index] for index in indices]


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    texts, labels = load_sms_data()
    splits = stratified_split(labels, seed=SEED)
    train_texts = select(texts, splits["train"])
    vocabulary = build_vocabulary(train_texts)

    datasets = {}
    for name, indices in splits.items():
        datasets[name] = SmsDataset(
            select(texts, indices), labels[indices], vocabulary, maximum_length=80
        )
    generator = torch.Generator().manual_seed(SEED)
    train_loader = DataLoader(
        datasets["train"], batch_size=64, shuffle=True, generator=generator
    )
    validation_loader = DataLoader(datasets["validation"], batch_size=128)
    test_loader = DataLoader(datasets["test"], batch_size=128)

    model = LstmClassifier(len(vocabulary), embedding_size=64, hidden_size=64)
    history, training_seconds, loss_function = train_model(
        model, train_loader, validation_loader, epochs=8, learning_rate=0.002, device=device
    )
    test_metrics = evaluate(model, test_loader, loss_function, device)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    result = {
        "model": "LSTM",
        "task": "UCI SMS spam classification",
        "seed": SEED,
        "device": str(device),
        "train_samples": len(datasets["train"]),
        "validation_samples": len(datasets["validation"]),
        "test_samples": len(datasets["test"]),
        "vocabulary_size": len(vocabulary),
        "maximum_sequence_length": 80,
        "parameter_count": parameter_count,
        "training_seconds": training_seconds,
        **{f"test_{key}": value for key, value in test_metrics.items()},
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / "metrics.json").open("w", encoding="utf-8") as output_file:
        json.dump(result, output_file, indent=2)
    with (OUTPUT_DIR / "training_history.csv").open(
        "w", encoding="utf-8", newline=""
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)

    print("\nLab 7 test result")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
