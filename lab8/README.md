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

## Measured comparison on this machine

Both best-validation-F1 checkpoints were evaluated on the same 838 test
messages.

| Measure | Lab 7 LSTM | Lab 8 BERT-tiny |
|---|---:|---:|
| Test accuracy | 98.21% | 98.57% |
| Test precision | 97.12% | 94.69% |
| Test recall | 89.38% | 94.69% |
| Test F1 | 93.09% | 94.69% |
| Parameters | 257,857 | 4,386,178 |
| CPU training time | 4.00 s | 14.98 s |
| CPU inference/message | 0.019 ms | 0.248 ms |

The transformer improves accuracy by **0.36 percentage points** and F1 by
**1.60 points**. Its stronger recall reduces missed spam from 12 messages to 6,
although false alarms rise from 3 to 6. The computation cost is much larger:
BERT-tiny has **17.01x** as many parameters, took **3.75x** as long to train and
was **12.76x** slower per message in this CPU run.

## Discussion

The pretrained transformer begins with general English representations and can
connect words using bidirectional self-attention. The LSTM reads sequentially
and learns its embedding from this small data set. BERT-tiny is therefore
expected to give strong accuracy with fewer task-specific examples, but it has
more parameters and self-attention performs more work per sequence. The final
conclusion uses the locally measured files rather than this expectation alone.

The measurements show that the transformer gives the better accuracy/F1 and a
more balanced precision-recall result. However, its small quality gain has a
large computation cost. For a high-volume, resource-limited spam filter, the
LSTM is a reasonable choice. When missed spam is more costly and resources are
available, the transformer is preferable.

## Conclusion

Pretraining and attention helped BERT-tiny generalize slightly better on this
small text data set, especially for spam recall. The LSTM remained remarkably
competitive and much cheaper. Architecture choice should therefore be based on
the error cost and deployment budget, not accuracy alone. Timings are specific
to this machine and can vary between runs.
