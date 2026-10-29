# MaterialSense measured experiment

Seed: 48. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **gradient_boosting / engineered**.
Held-out grouped RMSE: **5.912 MPa**; MAE: **4.198 MPa**; R2: **0.9004**; group-balanced RMSE: **6.253 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 19.201 | 15.436 | -0.0503 | 15.865 |
| grouped | ridge | raw | 11.408 | 9.371 | 0.6292 | 10.027 |
| grouped | random_forest | raw | 6.779 | 5.016 | 0.8691 | 6.542 |
| grouped | gradient_boosting | raw | 6.246 | 4.656 | 0.8889 | 6.243 |
| grouped | mean | engineered | 19.201 | 15.436 | -0.0503 | 15.865 |
| grouped | ridge | engineered | 7.682 | 6.062 | 0.8319 | 7.540 |
| grouped | random_forest | engineered | 6.120 | 4.412 | 0.8933 | 6.179 |
| grouped | gradient_boosting | engineered | 5.912 | 4.198 | 0.9004 | 6.253 |
| row_random_diagnostic | mean | raw | 16.971 | 13.505 | -0.0088 | 16.921 |
| row_random_diagnostic | ridge | raw | 10.027 | 7.855 | 0.6478 | 9.883 |
| row_random_diagnostic | random_forest | raw | 5.689 | 4.130 | 0.8866 | 5.745 |
| row_random_diagnostic | gradient_boosting | raw | 5.645 | 4.245 | 0.8884 | 5.778 |
| row_random_diagnostic | mean | engineered | 16.971 | 13.505 | -0.0088 | 16.921 |
| row_random_diagnostic | ridge | engineered | 7.085 | 5.490 | 0.8241 | 7.166 |
| row_random_diagnostic | random_forest | engineered | 5.458 | 3.984 | 0.8956 | 5.422 |
| row_random_diagnostic | gradient_boosting | engineered | 5.666 | 4.114 | 0.8875 | 5.774 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 230/236 (97.5%); whole-recipe coverage 80/86 (93.0%); mean width 26.925 MPa.
- group_max_cqr: row coverage 228/236 (96.6%); whole-recipe coverage 81/86 (94.2%); mean width 30.222 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
