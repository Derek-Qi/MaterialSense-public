# MaterialSense measured experiment

Seed: 43. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **5.846 MPa**; MAE: **4.009 MPa**; R2: **0.8810**; group-balanced RMSE: **6.141 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 16.949 | 13.842 | -0.0004 | 16.877 |
| grouped | ridge | raw | 10.303 | 8.385 | 0.6303 | 10.146 |
| grouped | random_forest | raw | 7.318 | 5.057 | 0.8135 | 7.134 |
| grouped | gradient_boosting | raw | 7.124 | 4.973 | 0.8233 | 7.696 |
| grouped | mean | engineered | 16.949 | 13.842 | -0.0004 | 16.877 |
| grouped | ridge | engineered | 6.750 | 4.917 | 0.8413 | 7.513 |
| grouped | random_forest | engineered | 5.846 | 4.009 | 0.8810 | 6.141 |
| grouped | gradient_boosting | engineered | 5.705 | 4.011 | 0.8866 | 6.508 |
| row_random_diagnostic | mean | raw | 16.899 | 13.650 | -0.0231 | 16.518 |
| row_random_diagnostic | ridge | raw | 10.660 | 8.452 | 0.5929 | 10.397 |
| row_random_diagnostic | random_forest | raw | 6.206 | 4.445 | 0.8620 | 6.224 |
| row_random_diagnostic | gradient_boosting | raw | 6.365 | 4.606 | 0.8549 | 6.623 |
| row_random_diagnostic | mean | engineered | 16.899 | 13.650 | -0.0231 | 16.518 |
| row_random_diagnostic | ridge | engineered | 7.377 | 5.639 | 0.8050 | 7.498 |
| row_random_diagnostic | random_forest | engineered | 5.972 | 4.191 | 0.8722 | 6.007 |
| row_random_diagnostic | gradient_boosting | engineered | 5.879 | 4.191 | 0.8762 | 6.200 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 184/194 (94.8%); whole-recipe coverage 79/86 (91.9%); mean width 24.749 MPa.
- group_max_cqr: row coverage 188/194 (96.9%); whole-recipe coverage 81/86 (94.2%); mean width 29.454 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
