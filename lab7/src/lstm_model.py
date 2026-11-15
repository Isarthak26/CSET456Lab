"""LSTM text classifier and training helpers for Lab 7."""

from __future__ import annotations

from time import perf_counter

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset

from data_utils import classification_metrics, encode_text


class SmsDataset(Dataset):
    def __init__(self, texts, labels, vocabulary, maximum_length=80):
        encoded = [encode_text(text, vocabulary, maximum_length) for text in texts]
        self.token_ids = torch.tensor([item[0] for item in encoded], dtype=torch.long)
        self.lengths = torch.tensor([item[1] for item in encoded], dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return self.token_ids[index], self.lengths[index], self.labels[index]


class LstmClassifier(nn.Module):
    def __init__(self, vocabulary_size: int, embedding_size=64, hidden_size=64):
        super().__init__()
        self.embedding = nn.Embedding(vocabulary_size, embedding_size, padding_idx=0)
        self.lstm = nn.LSTM(embedding_size, hidden_size, batch_first=True)
        self.dropout = nn.Dropout(0.30)
        self.output = nn.Linear(hidden_size, 1)

    def forward(self, token_ids, lengths):
        embedded = self.embedding(token_ids)
        packed = nn.utils.rnn.pack_padded_sequence(
            embedded, lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        _, (hidden, _) = self.lstm(packed)
        return self.output(self.dropout(hidden[-1])).squeeze(1)


def evaluate(model, data_loader, loss_function, device):
    model.eval()
    losses, labels, predictions = [], [], []
    started = perf_counter()
    with torch.no_grad():
        for token_ids, lengths, batch_labels in data_loader:
            token_ids = token_ids.to(device)
            lengths = lengths.to(device)
            batch_labels = batch_labels.to(device)
            logits = model(token_ids, lengths)
            losses.append(loss_function(logits, batch_labels).item() * len(batch_labels))
            labels.extend(batch_labels.cpu().numpy().astype(int).tolist())
            predictions.extend((torch.sigmoid(logits) >= 0.5).cpu().numpy().astype(int).tolist())
    elapsed = perf_counter() - started
    metrics = classification_metrics(labels, predictions)
    metrics["loss"] = float(sum(losses) / len(labels))
    metrics["inference_seconds"] = elapsed
    metrics["milliseconds_per_message"] = 1000.0 * elapsed / len(labels)
    return metrics


def train_model(model, train_loader, validation_loader, epochs, learning_rate, device):
    model.to(device)
    train_labels = train_loader.dataset.labels.numpy()
    negative_count = float(np.sum(train_labels == 0))
    positive_count = float(np.sum(train_labels == 1))
    loss_function = nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(negative_count / positive_count, device=device)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    history = []
    best_f1 = -1.0
    best_state = None
    started = perf_counter()
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for token_ids, lengths, labels in train_loader:
            token_ids, lengths, labels = (
                token_ids.to(device),
                lengths.to(device),
                labels.to(device),
            )
            optimizer.zero_grad()
            loss = loss_function(model(token_ids, lengths), labels)
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
            best_state = {name: value.detach().cpu().clone() for name, value in model.state_dict().items()}
    training_seconds = perf_counter() - started
    model.load_state_dict(best_state)
    return history, training_seconds, loss_function
