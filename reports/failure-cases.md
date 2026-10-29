# Recorded failure cases

Post-hoc descriptive examples from held-out groups; selected for large absolute error.
These cases never selected/tuned models. Repeated rows across seeds remain resplit observations.

| Seed / row | Age | Actual | Predicted | Abs. error | OOD flag | CQR covers? |
|---|---:|---:|---:|---:|---|---|
| 43 / 383 | 28 | 78.80 | 49.78 | 29.02 | True | False |
| 48 / 383 | 28 | 78.80 | 51.27 | 27.53 | False | False |
| 51 / 404 | 28 | 76.24 | 51.77 | 24.47 | False | False |
| 50 / 569 | 28 | 22.49 | 46.80 | 24.31 | False | True |
| 48 / 114 | 7 | 22.90 | 47.20 | 24.31 | False | True |
| 50 / 404 | 28 | 76.24 | 52.75 | 23.49 | False | False |
| 42 / 404 | 28 | 76.24 | 53.06 | 23.18 | True | False |
| 43 / 153 | 56 | 80.20 | 57.48 | 22.72 | True | False |

## Interpretation

Large errors can occur without an OOD warning; some flagged predictions have small error. At the
default threshold the mean error-event recall is only 29.1%, so a quiet warning is weak reassurance.
CQR can cover a bad point estimate because its quantile predictors are separate; wide intervals
can improve coverage while reducing usefulness. Width is not a probability of failure.

The complete cases, ingredient quantities, bounds and per-seed identifiers are in
[failures.csv](benchmark-10/failures.csv). Every test prediction, not just these examples, is saved
in benchmark-10/seed-*/reliability_predictions.csv. This dataset lacks laboratory/batch metadata,
so attributing any individual failure to a physical mechanism would require new evidence.
