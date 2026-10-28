# Lab 4 - Embeddings

This lab extends the BPE tokenizer and source-code corpus prepared in Lab 3. It
implements two original token-embedding approaches, skip-gram Word2Vec, and a
compact Code2Vec-style AST encoder. Every experiment is deterministic and saves
both its source code and result data.

## Requirements completed

- Selected 20 top-50 BPE tokens: 10 manually and 10 with seeded random sampling.
- Implemented two original embedding approaches.
- Calculated all 190 pairwise cosine similarities for each token approach.
- Reported and interpreted the five most similar pairs.
- Documented failure cases for both original representations.
- Implemented Word2Vec with skip-gram negative sampling.
- Implemented a Code2Vec-style AST path-context model.
- Saved source, embeddings, similarity rankings, training losses, prompts and a
  combined run transcript.

## Reproduce the lab

Run these commands from the repository root:

```bash
python3 -m venv lab4/.venv
lab4/.venv/bin/pip install -r lab4/requirements.txt
lab4/.venv/bin/python lab4/src/run_all.py
lab4/.venv/bin/python -m unittest discover -s lab4/tests -v
```

The existing `lab3/.venv` can also run the lab because it already contains the
same two dependencies.

## Token selection

The manual half covers declarations, control flow, imports, assertions and
values. The random half uses `random.Random(42)` over the remaining top-50
tokens, so another run selects the same sample.

| Selection | Tokens |
|---|---|
| Manual | `self`, `def`, `None`, `is`, `in`, `assert`, `for`, `if`, `import`, `return` |
| Seeded random | `0`, `,`, `):`, `X`, `[`, `the`, `:`, `)`, `==`, `'` |

The exact rank and corpus frequency of every token are in
`data/selected_20_tokens.csv`.

## Approach 1 - lexical-feature hashing

### Thought process

A source-code token contains useful internal evidence even before any corpus is
read. For example, `is` and `in` are short alphabetic keywords, while `):` and
`==` are two-character punctuation tokens. The method extracts boundary-aware
character 2-4 grams, identifier subtokens, length and lexical-shape features.
Each feature is mapped by SHA-256 into a signed 64-dimensional vector, after
which the vector is L2-normalized. SHA-256 is used instead of Python's changing
process hash, making the output reproducible.

### Five most similar pairs

| Rank | Pair | Cosine | Interpretation |
|---:|---|---:|---|
| 1 | `is` - `in` | 0.585369 | Sensible lexically: both are two-letter Python keywords beginning with `i`. |
| 2 | `):` - `==` | 0.503953 | Similar shape and length, but not similar program meaning. |
| 3 | `,` - `)` | 0.500000 | Both are single punctuation delimiters; semantic similarity is weak. |
| 4 | `X` - `the` | 0.447214 | Not meaningful; this exposes a hash collision/sparse-feature failure. |
| 5 | `,` - `[` | 0.433013 | Similar only at the broad punctuation level. |

### Failure cases

1. It cannot recognize semantic relationships with different spelling. For
   example, `def` and `return` work together but share few character features.
2. Sparse hashing can collide, producing the false `X` - `the` match.
3. Punctuation receives similar shape features even when operators and
   delimiters have different syntax roles (`):` - `==`).

## Approach 2 - PPMI-SVD repository context

### Thought process

Tokens used in similar neighborhoods tend to have related roles. The method
encodes up to one million Lab 3 BPE tokens without crossing file boundaries,
counts distance-weighted co-occurrences in a four-token window, converts counts
to positive pointwise mutual information (PPMI), and applies truncated SVD. The
result is a dense 32-dimensional embedding based on actual repository usage.

### Five most similar pairs

| Rank | Pair | Cosine | Interpretation |
|---:|---|---:|---|
| 1 | `in` - `for` | 0.802313 | Strongly sensible because Python loops commonly use `for ... in ...`. |
| 2 | `assert` - `==` | 0.801418 | Sensible because equality expressions are common assertions in tests. |
| 3 | `0` - `[` | 0.716204 | Partly sensible for indexing, but also affected by general frequency. |
| 4 | `self` - `return` | 0.593322 | Plausible inside instance methods, though not a direct semantic pair. |
| 5 | `self` - `):` | 0.584597 | Syntactically plausible in method signatures, but overly formatting-driven. |

### Failure cases

1. A small window learns formatting and syntax adjacency as well as meaning, so
   `self` - `):` ranks too highly.
2. Very frequent general tokens can dominate, as shown by `0` - `[`. PPMI
   reduces frequency bias but cannot remove it completely.
3. SVD compresses several meanings of one token into one vector; `in` as a loop
   keyword and `in` as a membership operator are not separated.

## Word2Vec

`src/word2vec_embedding.py` implements skip-gram with five negative samples,
48 dimensions, a context window of three, and three epochs. Training uses
300,000 positive pairs sampled from 750,000 Lab 3 tokens. The mean negative-
sampling loss decreases from **2.424343** to **2.113131**.

| Rank | Pair | Cosine |
|---:|---|---:|
| 1 | `def` - `return` | 0.697929 |
| 2 | `if` - `return` | 0.619792 |
| 3 | `assert` - `return` | 0.614233 |
| 4 | `assert` - `if` | 0.589515 |
| 5 | `def` - `assert` | 0.584053 |

Compared with lexical hashing, Word2Vec discovers relationships that do not
depend on spelling, especially `def` - `return`. Compared with PPMI-SVD, it
learns a predictive objective rather than directly factorizing corpus counts.
PPMI-SVD produces the clearest fixed syntax pairs (`for` - `in`, `assert` -
`==`), while Word2Vec groups tokens used across similar function and control-
flow regions. Both corpus approaches still merge multiple meanings and inherit
bias from the sampled repositories.

## Code2Vec

`src/code2vec_embedding.py` parses Python functions and extracts contexts of the
form `(start terminal, AST path, end terminal)`. Terminal and path vectors are
trained with negative sampling to predict the enclosing method name; mean
pooling then produces a 48-dimensional function vector. The run parsed 16 large
Python files into 350 functions and 23,880 path contexts. Training loss fell
from **3.299758** to **2.034973**.

The strongest pairs are structurally duplicated or near-duplicated functions:

1. `hide_available_pandas` - `hide_available_matplotlib`
2. `_available_if_estimator_has` - `_available_if_base_estimator_has`
3. two `__sklearn_tags__` implementations
4. two `get_params` implementations
5. two `set_params` implementations

Their cosine similarity is 1.0 because their sampled AST path-context bags are
identical. This is a useful success for structural similarity, while also
showing the model's limitation: mean pooling cannot distinguish functions with
the same structure but different library/API semantics. This implementation is
a compact educational Code2Vec-style model, not the pretrained Java Code2Vec
checkpoint from the original paper.

## Files

- `src/common.py`: corpus, cosine, normalization and CSV utilities.
- `src/feature_embedding.py`: original lexical-feature method.
- `src/cooccurrence_embedding.py`: original PPMI-SVD method.
- `src/word2vec_embedding.py`: NumPy skip-gram negative sampling.
- `src/code2vec_embedding.py`: Python AST path-context encoder.
- `src/run_all.py`: reproducible end-to-end runner.
- `data/*_embeddings.csv`: readable model vectors.
- `data/*_similarity.csv`: complete token rankings or top function rankings.
- `data/*_training.csv`: Word2Vec and Code2Vec loss histories.
- `output/`: prompt record, run transcript and evidence images.

## Reproducibility and limitations

All random operations use seed 42 or a stable SHA-256-derived seed. Results may
differ slightly across NumPy/BLAS versions because SVD floating-point signs and
rounding are implementation-dependent. The corpus is a limited sample of the
repositories collected in Lab 3, so conclusions should not be generalized to
all programming languages or projects.
