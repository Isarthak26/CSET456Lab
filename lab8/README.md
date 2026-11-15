# Lab 8 - SMS Spam Classification with an Open-Source Transformer

## Aim

To solve the same SMS spam-classification problem as Lab 7 with an open-source
transformer and compare predictive performance and computation.

## Selected transformer

The experiment fine-tunes
[`prajjwal1/bert-tiny`](https://huggingface.co/prajjwal1/bert-tiny), an MIT-licensed
compact BERT checkpoint. It has two transformer layers, hidden size 128 and two
attention heads. Its pretrained WordPiece vocabulary contains 30,522 tokens.
The small checkpoint was selected so that a student can run the experiment on a
CPU while still testing real transformer transfer learning.

## Fair comparison design

- same 5,574 UCI messages as Lab 7;
- same seed-42 stratified train/validation/test indices;
- same maximum sequence length of 80;
- weighted loss in both experiments;
- best checkpoint selected using validation F1;
- the same untouched 838-message test split;
- wall-clock training and complete-test inference measured on CPU.

Lab 7 uses its own word tokenizer, whereas BERT must use the WordPiece tokenizer
on which it was pretrained. This is an intentional model difference.

## Run

Run Lab 7 first so that its data and metrics exist. Then, from the repository
root:

```bash
python3.11 -m venv lab8/.venv
lab8/.venv/bin/pip install -r lab8/requirements.txt
lab8/.venv/bin/python lab8/src/run_experiment.py
lab8/.venv/bin/python -m unittest discover -s lab8/tests -v
```

The first run downloads the approximately 18 MB pretrained checkpoint. The
script writes transformer metrics, training history, a two-model comparison CSV
and calculated computation ratios to `output/`.

## What the comparison means

The pretrained transformer begins with general English representations and can
connect words using bidirectional self-attention. The LSTM reads sequentially
and learns its embedding from this small data set. BERT-tiny is therefore
expected to give strong accuracy with fewer task-specific examples, but it has
more parameters and self-attention performs more work per sequence. The final
conclusion uses the locally measured files rather than this expectation alone.
