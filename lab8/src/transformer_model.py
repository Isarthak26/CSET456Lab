"""BERT-tiny data, training and evaluation helpers for Lab 8."""

from __future__ import annotations

from time import perf_counter

import torch
from torch import nn
from torch.utils.data import Dataset

from data_utils import classification_metrics


class TransformerSmsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, maximum_length=80):
        self.encodings = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=maximum_length,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        item = {name: values[index] for name, values in self.encodings.items()}
        item["labels"] = self.labels[index]
        return item


def evaluate(model, data_loader, loss_function, device):
    model.eval()
    losses, labels, predictions = [], [], []
    started = perf_counter()
    with torch.no_grad():
        for batch in data_loader:
            batch_labels = batch.pop("labels").to(device)
            inputs = {name: values.to(device) for name, values in batch.items()}
            logits = model(**inputs).logits
            losses.append(loss_function(logits, batch_labels).item() * len(batch_labels))
            labels.extend(batch_labels.cpu().tolist())
            predictions.extend(torch.argmax(logits, dim=1).cpu().tolist())
    elapsed = perf_counter() - started
    metrics = classification_metrics(labels, predictions)
    metrics["loss"] = float(sum(losses) / len(labels))
    metrics["inference_seconds"] = elapsed
    metrics["milliseconds_per_message"] = 1000.0 * elapsed / len(labels)
    return metrics


def train_model(
    model,
    train_loader,
    validation_loader,
    epochs,
    learning_rate,
    device,
):
    train_labels = train_loader.dataset.labels
    counts = torch.bincount(train_labels, minlength=2).float()
    class_weights = counts.sum() / (2.0 * counts)
    loss_function = nn.CrossEntropyLoss(weight=class_weights.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    model.to(device)
    history = []
    best_f1 = -1.0
    best_state = None
    started = perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            labels = batch.pop("labels").to(device)
            inputs = {name: values.to(device) for name, values in batch.items()}
            optimizer.zero_grad()
            logits = model(**inputs).logits
            loss = loss_function(logits, labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item() * len(labels)
        validation = evaluate(model, validation_loader, loss_function, device)
        history.append(
            {
                "epoch": epoch,
                "train_loss": total_loss / len(train_loader.dataset),
                "validation_loss": validation["loss"],
                "validation_accuracy": validation["accuracy"],
                "validation_f1": validation["f1"],
            }
        )
        print(
            f"Epoch {epoch:02d}: train loss={history[-1]['train_loss']:.4f}, "
            f"validation accuracy={validation['accuracy']:.4f}, f1={validation['f1']:.4f}"
        )
        if validation["f1"] > best_f1:
            best_f1 = validation["f1"]
            best_state = {
                name: value.detach().cpu().clone()
                for name, value in model.state_dict().items()
            }

    training_seconds = perf_counter() - started
    model.load_state_dict(best_state)
    return history, training_seconds, loss_function


def build_comparison(lstm_metrics: dict, transformer_metrics: dict):
    """Return consistent rows and compute ratios for the final comparison."""
    keys = [
        "test_accuracy",
        "test_precision",
        "test_recall",
        "test_f1",
        "parameter_count",
        "training_seconds",
        "test_milliseconds_per_message",
    ]
    rows = []
    for metrics in (lstm_metrics, transformer_metrics):
        rows.append({"model": metrics["model"], **{key: metrics[key] for key in keys}})
    ratios = {
        "transformer_to_lstm_parameter_ratio": (
            transformer_metrics["parameter_count"] / lstm_metrics["parameter_count"]
        ),
        "transformer_to_lstm_training_time_ratio": (
            transformer_metrics["training_seconds"] / lstm_metrics["training_seconds"]
        ),
        "transformer_to_lstm_inference_time_ratio": (
            transformer_metrics["test_milliseconds_per_message"]
            / lstm_metrics["test_milliseconds_per_message"]
        ),
        "transformer_minus_lstm_accuracy": (
            transformer_metrics["test_accuracy"] - lstm_metrics["test_accuracy"]
        ),
        "transformer_minus_lstm_f1": (
            transformer_metrics["test_f1"] - lstm_metrics["test_f1"]
        ),
    }
    return rows, ratios
