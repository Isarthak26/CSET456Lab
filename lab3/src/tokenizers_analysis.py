import csv
import os
import re
import sys

import numpy as np

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import BpeTrainer


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "data",
    "all_repositories.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

EMBEDDING_DIM = 100
SUBWORD_VOCAB_SIZE = 10000
MIN_FREQUENCY = 2


# ---------------------------------------------------------
# Increase CSV field size limit
# ---------------------------------------------------------

def set_csv_field_limit():
    """
    Increase Python's CSV field size limit so that large
    source-code files can be read from the dataset.
    """

    max_int = sys.maxsize

    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = max_int // 10


# ---------------------------------------------------------
# Load source-code dataset
# ---------------------------------------------------------

def load_source_code(dataset_path):
    """
    Load source-code text from all_repositories.csv.

    Expected columns include:
    repository, file_name, file_path, file_extension,
    loc, file_size, content
    """

    texts = []

    set_csv_field_limit()

    with open(
        dataset_path,
        "r",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                "CSV file does not contain a header."
            )

        # Find the column containing source code.
        possible_columns = [
            "content",
            "source_code",
            "code",
            "text",
            "file_content"
        ]

        text_column = None

        for column in possible_columns:
            if column in reader.fieldnames:
                text_column = column
                break

        if text_column is None:
            raise ValueError(
                "Could not find source-code column. "
                f"Available columns: {reader.fieldnames}"
            )

        for row in reader:
            text = row.get(text_column, "")

            if text:
                texts.append(text)

    if not texts:
        raise ValueError(
            "No source-code text was found in the dataset."
        )

    return texts


# ---------------------------------------------------------
# Character-level tokenizer
# ---------------------------------------------------------

def character_tokenizer(text):
    """
    Character-level tokenization.

    Every character becomes one token.
    """

    return list(text)


# ---------------------------------------------------------
# Word-level tokenizer
# ---------------------------------------------------------

def word_tokenizer(text):
    """
    Word-level tokenizer.

    Words and punctuation marks are kept as separate tokens.
    """

    return re.findall(
        r"\w+|[^\w\s]",
        text,
        flags=re.UNICODE
    )


# ---------------------------------------------------------
# Subword-level tokenizer
# ---------------------------------------------------------

def train_subword_tokenizer(texts):
    """
    Train a BPE subword tokenizer using the Hugging Face
    tokenizers library.
    """

    tokenizer = Tokenizer(
        BPE(unk_token="[UNK]")
    )

    tokenizer.pre_tokenizer = Whitespace()

    trainer = BpeTrainer(
        vocab_size=SUBWORD_VOCAB_SIZE,
        min_frequency=MIN_FREQUENCY,
        special_tokens=["[UNK]"]
    )

    tokenizer.train_from_iterator(
        texts,
        trainer=trainer
    )

    return tokenizer


# ---------------------------------------------------------
# Calculate tokenizer statistics
# ---------------------------------------------------------

def calculate_stats(
    tokenizer_name,
    vocabulary_size,
    sequence_lengths,
    embedding_dim
):
    """
    Calculate vocabulary size, average sequence length,
    embedding matrix size, parameter count and memory.
    """

    average_sequence_length = (
        sum(sequence_lengths) / len(sequence_lengths)
    )

    embedding_parameters = (
        vocabulary_size * embedding_dim
    )

    embedding_memory_mb = (
        embedding_parameters * 4
    ) / (1024 * 1024)

    return {
        "tokenizer": tokenizer_name,
        "vocab_size": vocabulary_size,
        "average_sequence_length": average_sequence_length,
        "embedding_dim": embedding_dim,
        "embedding_matrix_shape": (
            f"({vocabulary_size}, {embedding_dim})"
        ),
        "embedding_parameters": embedding_parameters,
        "approx_embedding_memory_mb": (
            embedding_memory_mb
        )
    }


# ---------------------------------------------------------
# Save comparison results
# ---------------------------------------------------------

def save_comparison(results):
    """
    Save tokenizer comparison results as CSV.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(
        OUTPUT_DIR,
        "tokenizer_comparison.csv"
    )

    fieldnames = [
        "tokenizer",
        "vocab_size",
        "average_sequence_length",
        "embedding_dim",
        "embedding_matrix_shape",
        "embedding_parameters",
        "approx_embedding_memory_mb"
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)

    return output_path


# ---------------------------------------------------------
# Main experiment
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("LAB 3 - TOKENIZER ANALYSIS")
    print("=" * 70)

    # -----------------------------------------------------
    # Check dataset
    # -----------------------------------------------------

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    print("\nDataset:")
    print(DATASET_PATH)

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    print("\nLoading source-code dataset...")

    texts = load_source_code(DATASET_PATH)

    print(
        f"Number of source files: {len(texts):,}"
    )

    # -----------------------------------------------------
    # Character tokenizer
    # -----------------------------------------------------

    print("\n" + "-" * 70)
    print("1. CHARACTER-LEVEL TOKENIZER")
    print("-" * 70)

    character_sequences = [
        character_tokenizer(text)
        for text in texts
    ]

    character_vocab = set()

    for sequence in character_sequences:
        character_vocab.update(sequence)

    character_vocab_size = len(character_vocab)

    character_lengths = [
        len(sequence)
        for sequence in character_sequences
    ]

    character_stats = calculate_stats(
        "Character",
        character_vocab_size,
        character_lengths,
        EMBEDDING_DIM
    )

    print(
        f"Vocabulary size: "
        f"{character_stats['vocab_size']:,}"
    )

    print(
        f"Average sequence length: "
        f"{character_stats['average_sequence_length']:.2f}"
    )

    print(
        f"Embedding matrix: "
        f"{character_stats['embedding_matrix_shape']}"
    )

    print(
        f"Embedding parameters: "
        f"{character_stats['embedding_parameters']:,}"
    )

    print(
        f"Approx. embedding memory: "
        f"{character_stats['approx_embedding_memory_mb']:.2f} MB"
    )

    # -----------------------------------------------------
    # Word tokenizer
    # -----------------------------------------------------

    print("\n" + "-" * 70)
    print("2. WORD-LEVEL TOKENIZER")
    print("-" * 70)

    word_sequences = [
        word_tokenizer(text)
        for text in texts
    ]

    word_vocab = set()

    for sequence in word_sequences:
        word_vocab.update(sequence)

    word_vocab_size = len(word_vocab)

    word_lengths = [
        len(sequence)
        for sequence in word_sequences
    ]

    word_stats = calculate_stats(
        "Word",
        word_vocab_size,
        word_lengths,
        EMBEDDING_DIM
    )

    print(
        f"Vocabulary size: "
        f"{word_stats['vocab_size']:,}"
    )

    print(
        f"Average sequence length: "
        f"{word_stats['average_sequence_length']:.2f}"
    )

    print(
        f"Embedding matrix: "
        f"{word_stats['embedding_matrix_shape']}"
    )

    print(
        f"Embedding parameters: "
        f"{word_stats['embedding_parameters']:,}"
    )

    print(
        f"Approx. embedding memory: "
        f"{word_stats['approx_embedding_memory_mb']:.2f} MB"
    )

    # -----------------------------------------------------
    # Subword tokenizer
    # -----------------------------------------------------

    print("\n" + "-" * 70)
    print("3. SUBWORD-LEVEL TOKENIZER")
    print("-" * 70)

    print("\nTraining BPE tokenizer...")
    print(
        "This may take some time for a large dataset."
    )

    subword_tokenizer = train_subword_tokenizer(
        texts
    )

    subword_vocab_size = (
        subword_tokenizer.get_vocab_size()
    )

    subword_lengths = []

    for text in texts:
        encoded = subword_tokenizer.encode(text)
        subword_lengths.append(
            len(encoded.ids)
        )

    subword_stats = calculate_stats(
        "Subword",
        subword_vocab_size,
        subword_lengths,
        EMBEDDING_DIM
    )

    print(
        f"Vocabulary size: "
        f"{subword_stats['vocab_size']:,}"
    )

    print(
        f"Average sequence length: "
        f"{subword_stats['average_sequence_length']:.2f}"
    )

    print(
        f"Embedding matrix: "
        f"{subword_stats['embedding_matrix_shape']}"
    )

    print(
        f"Embedding parameters: "
        f"{subword_stats['embedding_parameters']:,}"
    )

    print(
        f"Approx. embedding memory: "
        f"{subword_stats['approx_embedding_memory_mb']:.2f} MB"
    )

    # -----------------------------------------------------
    # Save tokenizer
    # -----------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    tokenizer_path = os.path.join(
        OUTPUT_DIR,
        "subword_tokenizer.json"
    )

    subword_tokenizer.save(
        tokenizer_path
    )

    print(
        f"\nSubword tokenizer saved to:"
        f"\n{tokenizer_path}"
    )

    # -----------------------------------------------------
    # Save comparison
    # -----------------------------------------------------

    results = [
        character_stats,
        word_stats,
        subword_stats
    ]

    comparison_path = save_comparison(
        results
    )

    # -----------------------------------------------------
    # Final comparison
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("TOKENIZER COMPARISON")
    print("=" * 70)

    print(
        f"{'Tokenizer':<15}"
        f"{'Vocab Size':>15}"
        f"{'Avg Seq Length':>20}"
        f"{'Embedding Matrix':>25}"
    )

    print("-" * 75)

    for result in results:

        print(
            f"{result['tokenizer']:<15}"
            f"{result['vocab_size']:>15,}"
            f"{result['average_sequence_length']:>20.2f}"
            f"{result['embedding_matrix_shape']:>25}"
        )

    print("\nComparison saved to:")
    print(comparison_path)

    print("\n" + "=" * 70)
    print("EXERCISE 1 COMPLETE")
    print("=" * 70)


# ---------------------------------------------------------
# Program entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()