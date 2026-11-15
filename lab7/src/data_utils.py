"""Shared SMS data loading and deterministic split utilities for Labs 7 and 8."""

from __future__ import annotations

import re
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np


LAB_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = LAB_DIR / "data" / "SMSSpamCollection"
DATA_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
TOKEN_PATTERN = re.compile(r"[a-z0-9']+|[^\w\s]", re.IGNORECASE)


def download_dataset(path: Path = DATA_PATH) -> Path:
    """Download the public UCI SMS Spam Collection when it is not present."""
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    archive_path = path.parent / "sms_spam_collection.zip"
    print(f"Downloading SMS Spam Collection from {DATA_URL}")
    urllib.request.urlretrieve(DATA_URL, archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        member = next(name for name in archive.namelist() if name.endswith("SMSSpamCollection"))
        with archive.open(member) as source, path.open("wb") as destination:
            destination.write(source.read())
    archive_path.unlink()
    return path


def load_sms_data(path: Path = DATA_PATH, download: bool = True):
    if not path.exists():
        if not download:
            raise FileNotFoundError(f"Missing data set: {path}")
        download_dataset(path)
    texts, labels = [], []
    with path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            label, separator, text = line.rstrip("\n").partition("\t")
            if not separator or label not in {"ham", "spam"}:
                raise ValueError(f"Malformed row {line_number} in {path}")
            texts.append(text)
            labels.append(1 if label == "spam" else 0)
    return texts, np.asarray(labels, dtype=np.int64)


def stratified_split(labels: np.ndarray, seed: int = 42):
    """Create deterministic 70/15/15 indices while preserving class balance."""
    rng = np.random.default_rng(seed)
    split_ids = {"train": [], "validation": [], "test": []}
    for label in np.unique(labels):
        ids = np.flatnonzero(labels == label)
        rng.shuffle(ids)
        train_end = int(0.70 * len(ids))
        validation_end = int(0.85 * len(ids))
        split_ids["train"].extend(ids[:train_end])
        split_ids["validation"].extend(ids[train_end:validation_end])
        split_ids["test"].extend(ids[validation_end:])
    for values in split_ids.values():
        rng.shuffle(values)
    return {name: np.asarray(values, dtype=np.int64) for name, values in split_ids.items()}


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def build_vocabulary(
    texts: list[str], min_frequency: int = 2, maximum_size: int = 5_000
):
    counts = Counter(token for text in texts for token in tokenize(text))
    ordered = sorted(
        (item for item in counts.items() if item[1] >= min_frequency),
        key=lambda item: (-item[1], item[0]),
    )
    vocabulary = {"<PAD>": 0, "<UNK>": 1}
    for token, _ in ordered[: maximum_size - len(vocabulary)]:
        vocabulary[token] = len(vocabulary)
    return vocabulary


def encode_text(text: str, vocabulary: dict[str, int], maximum_length: int = 80):
    token_ids = [vocabulary.get(token, vocabulary["<UNK>"]) for token in tokenize(text)]
    token_ids = token_ids[:maximum_length]
    length = max(1, len(token_ids))
    token_ids.extend([vocabulary["<PAD>"]] * (maximum_length - len(token_ids)))
    return token_ids, length


def classification_metrics(labels, predictions):
    labels = np.asarray(labels, dtype=np.int64)
    predictions = np.asarray(predictions, dtype=np.int64)
    true_positive = int(np.sum((labels == 1) & (predictions == 1)))
    true_negative = int(np.sum((labels == 0) & (predictions == 0)))
    false_positive = int(np.sum((labels == 0) & (predictions == 1)))
    false_negative = int(np.sum((labels == 1) & (predictions == 0)))
    precision = true_positive / max(1, true_positive + false_positive)
    recall = true_positive / max(1, true_positive + false_negative)
    f1 = 2.0 * precision * recall / max(1e-12, precision + recall)
    return {
        "accuracy": float((true_positive + true_negative) / len(labels)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }
