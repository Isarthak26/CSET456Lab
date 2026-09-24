import csv
import random
import numpy as np

INPUT_FILE = "data/selected_20_tokens.csv"
OUTPUT_FILE = "data/random_embeddings.npy"

EMBEDDING_DIMENSION = 50
RANDOM_SEED = 42


def load_tokens():
    tokens = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tokens.append(row["token"])

    return tokens


def generate_embeddings(tokens):
    random.seed(RANDOM_SEED)

    embeddings = {}

    for token in tokens:
        embeddings[token] = [
            random.uniform(-1, 1)
            for _ in range(EMBEDDING_DIMENSION)
        ]

    return embeddings


def main():
    tokens = load_tokens()

    embeddings = generate_embeddings(tokens)

    np.save(
        OUTPUT_FILE,
        embeddings,
        allow_pickle=True
    )

    print(f"Generated embeddings for {len(tokens)} tokens.")
    print(f"Embedding dimension: {EMBEDDING_DIMENSION}")
    print(f"Saved embeddings to: {OUTPUT_FILE}")

    for token, vector in embeddings.items():
        print(f"\nToken: {token}")
        print(f"Vector: {vector}")


if __name__ == "__main__":
    main()