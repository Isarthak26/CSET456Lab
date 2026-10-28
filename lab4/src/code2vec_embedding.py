"""A compact Code2Vec-style AST path-context encoder implemented with NumPy."""

from __future__ import annotations

import ast
import csv
import hashlib
import itertools
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from common import DATA_DIR, iter_source_rows, normalize_rows, rank_pairs
from word2vec_embedding import _sigmoid


RANDOM_SEED = 42
MAX_FILES = 250
MAX_FUNCTIONS = 350
MAX_CONTEXTS_PER_FUNCTION = 80
MAX_TERMINALS = 1_200
MAX_PATHS = 1_200
EMBEDDING_DIMENSION = 48
NEGATIVE_SAMPLES = 5
EPOCHS = 4
BATCH_SIZE = 256
LEARNING_RATE = 0.02


@dataclass(frozen=True)
class PathContext:
    start: str
    path: str
    end: str


@dataclass
class FunctionExample:
    identifier: str
    method_name: str
    contexts: list[PathContext]


def _stable_seed(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")


def _terminal_value(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.arg):
        return node.arg
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.alias):
        return node.name
    if isinstance(node, ast.keyword) and node.arg:
        return node.arg
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        if isinstance(node.value, bool):
            return str(node.value)
        if isinstance(node.value, (int, float)):
            return str(node.value)
        if isinstance(node.value, str):
            return "<str>"
    return None


def _walk_function(root: ast.AST) -> list[ast.AST]:
    """Walk one function body without mixing in nested function bodies."""

    nodes: list[ast.AST] = []
    stack = [root]
    while stack:
        node = stack.pop()
        nodes.append(node)
        children = list(ast.iter_child_nodes(node))
        for child in reversed(children):
            if child is not root and isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
            ):
                continue
            stack.append(child)
    return nodes


def _ast_path(
    start: ast.AST,
    end: ast.AST,
    parents: dict[ast.AST, ast.AST],
    root: ast.AST,
    max_length: int = 10,
) -> str | None:
    def ancestors(node: ast.AST) -> list[ast.AST]:
        result = [node]
        while result[-1] is not root and result[-1] in parents:
            result.append(parents[result[-1]])
        return result

    start_ancestors = ancestors(start)
    end_ancestors = ancestors(end)
    end_positions = {node: index for index, node in enumerate(end_ancestors)}
    common = next((node for node in start_ancestors if node in end_positions), None)
    if common is None:
        return None

    left = start_ancestors[: start_ancestors.index(common) + 1]
    right = end_ancestors[: end_positions[common]]
    if len(left) + len(right) > max_length:
        return None
    up = "^".join(type(node).__name__ for node in left)
    down = "v".join(type(node).__name__ for node in reversed(right))
    return f"{up}|{down}" if down else up


def extract_functions_from_source(
    repository: str,
    file_path: str,
    source: str,
    *,
    max_contexts: int = MAX_CONTEXTS_PER_FUNCTION,
) -> list[FunctionExample]:
    """Extract terminal-to-terminal AST path contexts from Python functions."""

    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []

    examples: list[FunctionExample] = []
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        nodes = _walk_function(function)
        parents = {
            child: parent
            for parent in nodes
            for child in ast.iter_child_nodes(parent)
            if child in nodes
        }
        terminals = [(node, _terminal_value(node)) for node in nodes]
        terminals = [(node, value) for node, value in terminals if value is not None]
        if len(terminals) < 2:
            continue

        candidate_pairs = list(itertools.combinations(range(len(terminals)), 2))
        identifier = (
            f"{repository}:{file_path}:{function.name}:"
            f"{getattr(function, 'lineno', 0)}"
        )
        if len(candidate_pairs) > max_contexts * 3:
            rng = np.random.default_rng(_stable_seed(identifier))
            chosen = rng.choice(len(candidate_pairs), size=max_contexts * 3, replace=False)
            candidate_pairs = [candidate_pairs[index] for index in chosen]

        contexts: list[PathContext] = []
        for left, right in candidate_pairs:
            start_node, start_value = terminals[left]
            end_node, end_value = terminals[right]
            path = _ast_path(start_node, end_node, parents, function)
            if path:
                contexts.append(PathContext(start_value, path, end_value))
            if len(contexts) >= max_contexts:
                break

        if contexts:
            examples.append(
                FunctionExample(
                    identifier=identifier,
                    method_name=function.name,
                    contexts=contexts,
                )
            )
    return examples


def load_function_examples(
    *,
    max_files: int = MAX_FILES,
    max_functions: int = MAX_FUNCTIONS,
) -> tuple[list[FunctionExample], int]:
    examples: list[FunctionExample] = []
    parsed_files = 0
    for row in iter_source_rows(max_files=max_files, python_only=True):
        parsed_files += 1
        examples.extend(
            extract_functions_from_source(
                row["repository"], row["file_path"], row["source_code"]
            )
        )
        if len(examples) >= max_functions:
            return examples[:max_functions], parsed_files
    return examples, parsed_files


def _limited_vocabulary(values: list[str], limit: int) -> list[str]:
    return ["<UNK>", *[value for value, _ in Counter(values).most_common(limit - 1)]]


def vectorize_examples(examples: list[FunctionExample]) -> tuple[dict[str, object], ...]:
    terminals = [
        terminal
        for example in examples
        for context in example.contexts
        for terminal in (context.start, context.end)
    ]
    paths = [context.path for example in examples for context in example.contexts]
    terminal_vocab = _limited_vocabulary(terminals, MAX_TERMINALS)
    path_vocab = _limited_vocabulary(paths, MAX_PATHS)
    target_vocab = sorted({example.method_name for example in examples})

    terminal_index = {value: index for index, value in enumerate(terminal_vocab)}
    path_index = {value: index for index, value in enumerate(path_vocab)}
    target_index = {value: index for index, value in enumerate(target_vocab)}

    start_ids: list[int] = []
    path_ids: list[int] = []
    end_ids: list[int] = []
    target_ids: list[int] = []
    function_ids: list[int] = []
    for function_id, example in enumerate(examples):
        for context in example.contexts:
            start_ids.append(terminal_index.get(context.start, 0))
            path_ids.append(path_index.get(context.path, 0))
            end_ids.append(terminal_index.get(context.end, 0))
            target_ids.append(target_index[example.method_name])
            function_ids.append(function_id)

    arrays = tuple(
        np.asarray(values, dtype=np.int64)
        for values in (start_ids, path_ids, end_ids, target_ids, function_ids)
    )
    metadata: dict[str, object] = {
        "terminal_vocab": terminal_vocab,
        "path_vocab": path_vocab,
        "target_vocab": target_vocab,
    }
    return metadata, *arrays


def train_code2vec(
    start_ids: np.ndarray,
    path_ids: np.ndarray,
    end_ids: np.ndarray,
    target_ids: np.ndarray,
    *,
    terminal_count: int,
    path_count: int,
    target_count: int,
    dimension: int = EMBEDDING_DIMENSION,
    negative_samples: int = NEGATIVE_SAMPLES,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    seed: int = RANDOM_SEED,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[float]]:
    """Train path-context vectors to predict their enclosing method name."""

    if len(start_ids) == 0 or target_count < 2:
        raise ValueError("Code2Vec training needs contexts from at least two targets.")

    rng = np.random.default_rng(seed)
    scale = 0.5 / dimension
    terminal_embeddings = rng.uniform(
        -scale, scale, size=(terminal_count, dimension)
    )
    path_embeddings = rng.uniform(-scale, scale, size=(path_count, dimension))
    target_embeddings = np.zeros((target_count, dimension), dtype=np.float64)
    order = np.arange(len(start_ids))
    losses: list[float] = []

    for epoch in range(epochs):
        rng.shuffle(order)
        total_loss = 0.0
        examples_seen = 0
        rate = learning_rate * max(0.25, 1.0 - 0.75 * epoch / max(epochs, 1))

        for offset in range(0, len(order), batch_size):
            indices = order[offset : offset + batch_size]
            starts = start_ids[indices]
            paths = path_ids[indices]
            ends = end_ids[indices]
            positives = target_ids[indices]
            negative_ids = rng.integers(
                0, target_count, size=(len(indices), negative_samples)
            )

            start_vectors = terminal_embeddings[starts].copy()
            path_vectors = path_embeddings[paths].copy()
            end_vectors = terminal_embeddings[ends].copy()
            pre_activation = (start_vectors + path_vectors + end_vectors) / 3.0
            contexts = np.tanh(pre_activation)

            positive_vectors = target_embeddings[positives].copy()
            negative_vectors = target_embeddings[negative_ids].copy()
            positive_probabilities = _sigmoid(
                np.sum(contexts * positive_vectors, axis=1)
            )
            negative_probabilities = _sigmoid(
                np.einsum("bd,bkd->bk", contexts, negative_vectors)
            )
            total_loss += float(
                -np.log(positive_probabilities + 1e-12).sum()
                - np.log(1.0 - negative_probabilities + 1e-12).sum()
            )
            examples_seen += len(indices)

            positive_error = positive_probabilities - 1.0
            negative_error = negative_probabilities
            context_gradient = (
                positive_error[:, None] * positive_vectors
                + np.einsum("bk,bkd->bd", negative_error, negative_vectors)
            )
            component_gradient = context_gradient * (1.0 - contexts**2) / 3.0
            positive_gradient = positive_error[:, None] * contexts
            negative_gradient = negative_error[:, :, None] * contexts[:, None, :]

            clipped_component = np.clip(component_gradient, -2.0, 2.0)
            np.add.at(terminal_embeddings, starts, -rate * clipped_component)
            np.add.at(path_embeddings, paths, -rate * clipped_component)
            np.add.at(terminal_embeddings, ends, -rate * clipped_component)
            np.add.at(
                target_embeddings,
                positives,
                -rate * np.clip(positive_gradient, -2.0, 2.0),
            )
            np.add.at(
                target_embeddings,
                negative_ids.reshape(-1),
                -rate
                * np.clip(negative_gradient, -2.0, 2.0).reshape(-1, dimension),
            )

        losses.append(total_loss / max(examples_seen, 1))
        print(f"Code2Vec epoch {epoch + 1}/{epochs}: mean loss={losses[-1]:.6f}")

    return terminal_embeddings, path_embeddings, target_embeddings, losses


def pool_function_embeddings(
    start_ids: np.ndarray,
    path_ids: np.ndarray,
    end_ids: np.ndarray,
    function_ids: np.ndarray,
    terminal_embeddings: np.ndarray,
    path_embeddings: np.ndarray,
    function_count: int,
) -> np.ndarray:
    context_vectors = np.tanh(
        (
            terminal_embeddings[start_ids]
            + path_embeddings[path_ids]
            + terminal_embeddings[end_ids]
        )
        / 3.0
    )
    pooled = np.zeros((function_count, context_vectors.shape[1]), dtype=np.float64)
    counts = np.zeros(function_count, dtype=np.float64)
    np.add.at(pooled, function_ids, context_vectors)
    np.add.at(counts, function_ids, 1.0)
    pooled /= np.maximum(counts[:, None], 1.0)
    return normalize_rows(pooled)


def _save_function_embeddings(
    examples: list[FunctionExample], embeddings: np.ndarray
) -> None:
    with (DATA_DIR / "code2vec_function_embeddings.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["function", "method_name", *[f"dim_{index:02d}" for index in range(embeddings.shape[1])]]
        )
        for example, vector in zip(examples, embeddings, strict=True):
            writer.writerow(
                [
                    example.identifier,
                    example.method_name,
                    *[f"{float(value):.8f}" for value in vector],
                ]
            )


def _save_context_sample(examples: list[FunctionExample]) -> None:
    with (DATA_DIR / "code2vec_path_contexts.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["function", "start_terminal", "ast_path", "end_terminal"])
        written = 0
        for example in examples:
            for context in example.contexts:
                writer.writerow(
                    [example.identifier, context.start, context.path, context.end]
                )
                written += 1
                if written >= 500:
                    return


def main() -> None:
    examples, parsed_files = load_function_examples()
    metadata, start_ids, path_ids, end_ids, target_ids, function_ids = vectorize_examples(
        examples
    )
    terminal_vocab = metadata["terminal_vocab"]
    path_vocab = metadata["path_vocab"]
    target_vocab = metadata["target_vocab"]

    terminal_embeddings, path_embeddings, _, losses = train_code2vec(
        start_ids,
        path_ids,
        end_ids,
        target_ids,
        terminal_count=len(terminal_vocab),
        path_count=len(path_vocab),
        target_count=len(target_vocab),
    )
    function_embeddings = pool_function_embeddings(
        start_ids,
        path_ids,
        end_ids,
        function_ids,
        terminal_embeddings,
        path_embeddings,
        len(examples),
    )
    labels = [example.identifier for example in examples]
    pairs = rank_pairs(labels, function_embeddings)

    _save_function_embeddings(examples, function_embeddings)
    _save_context_sample(examples)
    with (DATA_DIR / "code2vec_similarity.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "function_1", "function_2", "cosine_similarity"])
        for rank, (left, right, similarity) in enumerate(pairs[:100], start=1):
            writer.writerow([rank, left, right, f"{similarity:.8f}"])
    with (DATA_DIR / "code2vec_training.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["epoch", "mean_negative_sampling_loss"])
        writer.writerows((index, f"{loss:.8f}") for index, loss in enumerate(losses, 1))

    print(
        f"Parsed {parsed_files} Python files into {len(examples)} functions and "
        f"{len(start_ids):,} path contexts."
    )
    print("\nCode2Vec - top 5 similar function pairs")
    for rank, (left, right, similarity) in enumerate(pairs[:5], start=1):
        print(f"{rank}. {left} <-> {right}: {similarity:.6f}")


if __name__ == "__main__":
    main()
