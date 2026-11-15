# Lab 7 - SMS Spam Classification with LSTM

## Aim

To apply a Long Short-Term Memory (LSTM) network to a sequence-classification
task and measure its performance.

## Task and data set

The selected task is classifying an SMS as **ham** or **spam**. The experiment
uses the public UCI SMS Spam Collection (5,574 messages). On the first run, the
script downloads it from UCI into `data/`. A seeded, class-stratified 70/15/15
split is used. The vocabulary is built from the training split only, preventing
test-data leakage.

Source: [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)

## LSTM design

- lowercase word/punctuation tokenizer;
- 5,000-token maximum vocabulary and 80-token sequences;
- 64-dimensional trainable embedding;
- one 64-unit LSTM layer;
- 30% dropout and one sigmoid-compatible output logit;
- weighted binary cross-entropy to handle the smaller spam class;
- Adam optimizer, gradient clipping and best validation-F1 checkpoint.

## Run

From the repository root:

```bash
python3.11 -m venv lab7/.venv
lab7/.venv/bin/pip install -r lab7/requirements.txt
lab7/.venv/bin/python lab7/src/run_experiment.py
lab7/.venv/bin/python -m unittest discover -s lab7/tests -v
```

Results are written to `output/metrics.json` and `output/training_history.csv`.
Accuracy is reported together with precision, recall and F1 because the classes
are imbalanced. Parameter count, training time and per-message inference time
are saved for the direct transformer comparison in Lab 8.

## Expected observation

The LSTM reads tokens in order and is much smaller than a pretrained language
model. It should learn spam indicators such as prizes, calls and numbers, but it
starts with random embeddings and must learn language patterns only from this
small data set. Consequently, it is computationally light but may miss unusual
phrasing that a pretrained transformer already understands.
