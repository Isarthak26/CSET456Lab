# Prompt record

This file records the prompts behind the implementation. It is kept as text so
the experiment is auditable. The submitted chat screenshots should show the
same wording without exposing account details or unrelated conversations.

## Overall task prompt

> I am a fourth-year student and tomorrow is my lab. I need to complete Lab 4
> and Lab 5 in the CSET456Lab repository, commit regularly, and keep Lab 5
> separate from Lab 4.

## Experiment 1 prompt - lexical features

> Create a deterministic embedding for the selected code tokens using only
> information inside each token. Combine character n-grams, identifier
> subtokens, token length, and lexical-shape features; hash them into a fixed
> vector; then report all cosine similarities and the top five pairs.

## Experiment 2 prompt - repository context

> Create a second embedding from how the selected tokens occur in the Lab 3
> source-code corpus. Build a windowed co-occurrence matrix, transform it with
> positive PMI, reduce it with SVD, and report all cosine similarities and the
> top five pairs.

## Word2Vec prompt

> Implement skip-gram Word2Vec with negative sampling using the Lab 3 BPE
> tokens. Use deterministic seeds, save the training loss and selected-token
> embeddings, and compare the result with both original approaches.

## Code2Vec prompt

> Implement a compact Code2Vec-style encoder for Python. Extract AST
> terminal-to-terminal path contexts, train those contexts to predict method
> names with negative sampling, pool contexts into function embeddings, and
> report the most similar functions.
