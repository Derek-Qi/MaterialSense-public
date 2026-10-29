# MaterialSense measured experiment

Seed: 46. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **4.243 MPa**; MAE: **3.228 MPa**; R2: **0.9120**; group-balanced RMSE: **4.340 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 15.148 | 12.596 | -0.1218 | 14.865 |
| grouped | ridge | raw | 9.128 | 7.440 | 0.5927 | 8.782 |
| grouped | random_forest | raw | 4.976 | 3.843 | 0.8790 | 4.985 |
| grouped | gradient_boosting | raw | 5.594 | 4.297 | 0.8470 | 6.098 |
| grouped | mean | engineered | 15.148 | 12.596 | -0.1218 | 14.865 |
| grouped | ridge | engineered | 5.652 | 4.212 | 0.8439 | 6.064 |
| grouped | random_forest | engineered | 4.243 | 3.228 | 0.9120 | 4.340 |
| grouped | gradient_boosting | engineered | 4.537 | 3.362 | 0.8994 | 5.017 |
| row_random_diagnostic | mean | raw | 16.818 | 13.360 | -0.0005 | 16.290 |
| row_random_diagnostic | ridge | raw | 10.449 | 8.291 | 0.6138 | 9.805 |
| row_random_diagnostic | random_forest | raw | 4.842 | 3.596 | 0.9171 | 4.790 |
| row_random_diagnostic | gradient_boosting | raw | 4.662 | 3.545 | 0.9231 | 4.607 |
| row_random_diagnostic | mean | engineered | 16.818 | 13.360 | -0.0005 | 16.290 |
| row_random_diagnostic | ridge | engineered | 7.045 | 5.594 | 0.8245 | 6.842 |
| row_random_diagnostic | random_forest | engineered | 4.959 | 3.532 | 0.9130 | 4.754 |
| row_random_diagnostic | gradient_boosting | engineered | 4.818 | 3.614 | 0.9179 | 4.680 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 198/202 (98.0%); whole-recipe coverage 82/86 (95.3%); mean width 22.318 MPa.
- group_max_cqr: row coverage 199/202 (98.5%); whole-recipe coverage 83/86 (96.5%); mean width 24.124 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
