# Lab 6 - Same Nodes, Different Neural Network Depth

## Aim

To study how changing neural-network depth affects learning speed when the total
number of hidden nodes stays fixed at 30.

## Task and data

The task is binary classification on a noisy **two-moons** data set. It is a
useful small problem because a straight line cannot separate the two classes.
The script generates 1,200 samples with seed 42 and uses a 70/15/15 split. Only
training-set statistics are used for standardization.

## Architectures

| Model | Hidden layers | Total hidden nodes |
|---|---:|---:|
| Shallow | 30 | 30 |
| Deep | 10, 10, 10 | 30 |

Both models use ReLU hidden activations, sigmoid output, binary cross-entropy
and Adam. The hidden-node count is controlled, but the parameter count is also
reported because depth changes the number of connections.

## Correctness checks

1. Finite-difference gradient checking verifies the backpropagation equations.
2. Unit tests check output shape, probability range, the 30-node constraint and
   whether a small model learns above 85% validation accuracy.
3. The final experiment evaluates untouched test data.

## Run

From the repository root:

```bash
python3.11 -m venv lab6/.venv
lab6/.venv/bin/pip install -r lab6/requirements.txt
lab6/.venv/bin/python lab6/src/run_experiment.py
lab6/.venv/bin/python -m unittest discover -s lab6/tests -v
```

The generated `output/architecture_comparison.csv` reports test accuracy and
the epoch/wall-clock time at which each model first reaches 90% validation
accuracy. The two history CSV files contain complete learning curves.

## Observation

Depth does not automatically make a small network faster. The shallow model
has a more direct gradient path, whereas the deep model can create more stages
of nonlinear representation. On this simple two-dimensional task, the extra
depth is usually unnecessary overhead. Exact timings depend on the computer,
so the CSV generated on the submitted machine is the evidence used here.

## Conclusion

Keeping the node budget fixed does not keep the architecture or parameter count
identical. Layer arrangement changes optimization, computation and accuracy;
therefore both epoch-to-target and time-to-target should be compared instead of
looking only at final accuracy.
