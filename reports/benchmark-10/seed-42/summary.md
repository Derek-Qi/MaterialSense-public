# MaterialSense measured experiment

Seed: 42. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **5.217 MPa**; MAE: **3.887 MPa**; R2: **0.8865**; group-balanced RMSE: **5.584 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 15.551 | 12.353 | -0.0082 | 14.815 |
| grouped | ridge | raw | 10.070 | 7.995 | 0.5772 | 9.467 |
| grouped | random_forest | raw | 5.977 | 4.294 | 0.8511 | 6.114 |
| grouped | gradient_boosting | raw | 5.619 | 4.078 | 0.8684 | 5.909 |
| grouped | mean | engineered | 15.551 | 12.353 | -0.0082 | 14.815 |
| grouped | ridge | engineered | 6.410 | 4.956 | 0.8287 | 7.036 |
| grouped | random_forest | engineered | 5.217 | 3.887 | 0.8865 | 5.584 |
| grouped | gradient_boosting | engineered | 5.115 | 3.783 | 0.8909 | 5.722 |
| row_random_diagnostic | mean | raw | 16.070 | 13.079 | -0.0022 | 16.095 |
| row_random_diagnostic | ridge | raw | 9.818 | 7.775 | 0.6259 | 9.264 |
| row_random_diagnostic | random_forest | raw | 5.635 | 4.178 | 0.8768 | 5.687 |
| row_random_diagnostic | gradient_boosting | raw | 5.230 | 3.896 | 0.8939 | 5.327 |
| row_random_diagnostic | mean | engineered | 16.070 | 13.079 | -0.0022 | 16.095 |
| row_random_diagnostic | ridge | engineered | 6.393 | 5.141 | 0.8414 | 6.254 |
| row_random_diagnostic | random_forest | engineered | 5.282 | 3.724 | 0.8917 | 5.402 |
| row_random_diagnostic | gradient_boosting | engineered | 5.141 | 3.614 | 0.8974 | 5.221 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 220/232 (94.8%); whole-recipe coverage 77/86 (89.5%); mean width 21.219 MPa.
- group_max_cqr: row coverage 226/232 (97.4%); whole-recipe coverage 81/86 (94.2%); mean width 29.815 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
