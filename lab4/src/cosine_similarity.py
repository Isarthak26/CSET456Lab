import csv
import numpy as np

INPUT_TOKENS = "data/selected_20_tokens.csv"
INPUT_EMBEDDINGS = "data/random_embeddings.npy"
OUTPUT_FILE = "data/cosine_similarity.csv"


def load_tokens():
    tokens = []

    with open(INPUT_TOKENS, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tokens.append(row["token"])

    return tokens


def cosine_similarity(vector_a, vector_b):
    dot_product = np.dot(vector_a, vector_b)

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    return dot_product / (norm_a * norm_b)


def main():
    tokens = load_tokens()

    embeddings = np.load(
        INPUT_EMBEDDINGS,
        allow_pickle=True
    ).item()

    results = []

    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens)):

            token_a = tokens[i]
            token_b = tokens[j]

            similarity = cosine_similarity(
                embeddings[token_a],
                embeddings[token_b]
            )

            results.append(
                (token_a, token_b, similarity)
            )

    results.sort(key=lambda x: x[2], reverse=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            ["token_1", "token_2", "cosine_similarity"]
        )

        for token_a, token_b, similarity in results:
            writer.writerow(
                [token_a, token_b, round(similarity, 6)]
            )

    print(f"Compared {len(tokens)} tokens.")
    print(f"Total pairs: {len(results)}")
    print(f"Saved results to: {OUTPUT_FILE}")

    print("\nTop 5 most similar pairs:")

    for token_a, token_b, similarity in results[:5]:
        print(
            f"{token_a} <-> {token_b}: "
            f"{similarity:.6f}"
        )


if __name__ == "__main__":
    main()