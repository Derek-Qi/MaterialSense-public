# MaterialSense measured experiment

Seed: 44. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **5.889 MPa**; MAE: **4.446 MPa**; R2: **0.8617**; group-balanced RMSE: **5.829 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 15.907 | 12.967 | -0.0092 | 14.402 |
| grouped | ridge | raw | 10.673 | 8.510 | 0.5457 | 9.757 |
| grouped | random_forest | raw | 7.071 | 5.355 | 0.8006 | 6.064 |
| grouped | gradient_boosting | raw | 7.284 | 5.667 | 0.7884 | 6.549 |
| grouped | mean | engineered | 15.907 | 12.967 | -0.0092 | 14.402 |
| grouped | ridge | engineered | 8.071 | 6.407 | 0.7402 | 8.051 |
| grouped | random_forest | engineered | 5.889 | 4.446 | 0.8617 | 5.829 |
| grouped | gradient_boosting | engineered | 6.191 | 4.674 | 0.8471 | 6.046 |
| row_random_diagnostic | mean | raw | 16.612 | 13.102 | -0.0097 | 15.513 |
| row_random_diagnostic | ridge | raw | 10.701 | 8.283 | 0.5810 | 10.375 |
| row_random_diagnostic | random_forest | raw | 5.780 | 3.936 | 0.8778 | 5.805 |
| row_random_diagnostic | gradient_boosting | raw | 5.544 | 3.800 | 0.8875 | 5.707 |
| row_random_diagnostic | mean | engineered | 16.612 | 13.102 | -0.0097 | 15.513 |
| row_random_diagnostic | ridge | engineered | 6.735 | 5.183 | 0.8340 | 6.699 |
| row_random_diagnostic | random_forest | engineered | 5.350 | 3.786 | 0.8953 | 5.341 |
| row_random_diagnostic | gradient_boosting | engineered | 5.169 | 3.679 | 0.9022 | 5.238 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 172/192 (89.6%); whole-recipe coverage 73/86 (84.9%); mean width 20.824 MPa.
- group_max_cqr: row coverage 179/192 (93.2%); whole-recipe coverage 77/86 (89.5%); mean width 26.679 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
