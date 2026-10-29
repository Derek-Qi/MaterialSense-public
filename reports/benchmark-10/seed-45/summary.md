# MaterialSense measured experiment

Seed: 45. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **gradient_boosting / engineered**.
Held-out grouped RMSE: **6.906 MPa**; MAE: **5.343 MPa**; R2: **0.8680**; group-balanced RMSE: **6.590 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 19.406 | 15.347 | -0.0420 | 17.178 |
| grouped | ridge | raw | 12.099 | 9.867 | 0.5950 | 11.144 |
| grouped | random_forest | raw | 7.464 | 5.804 | 0.8459 | 7.333 |
| grouped | gradient_boosting | raw | 7.045 | 5.430 | 0.8627 | 7.161 |
| grouped | mean | engineered | 19.406 | 15.347 | -0.0420 | 17.178 |
| grouped | ridge | engineered | 8.176 | 6.450 | 0.8150 | 8.500 |
| grouped | random_forest | engineered | 6.709 | 5.092 | 0.8755 | 6.587 |
| grouped | gradient_boosting | engineered | 6.906 | 5.343 | 0.8680 | 6.590 |
| row_random_diagnostic | mean | raw | 16.921 | 13.733 | -0.0043 | 17.006 |
| row_random_diagnostic | ridge | raw | 10.879 | 8.441 | 0.5848 | 10.577 |
| row_random_diagnostic | random_forest | raw | 5.870 | 4.195 | 0.8791 | 5.980 |
| row_random_diagnostic | gradient_boosting | raw | 5.570 | 4.171 | 0.8912 | 5.772 |
| row_random_diagnostic | mean | engineered | 16.921 | 13.733 | -0.0043 | 17.006 |
| row_random_diagnostic | ridge | engineered | 7.124 | 5.526 | 0.8220 | 7.219 |
| row_random_diagnostic | random_forest | engineered | 5.277 | 3.645 | 0.9023 | 5.375 |
| row_random_diagnostic | gradient_boosting | engineered | 5.131 | 3.626 | 0.9077 | 5.263 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 199/212 (93.9%); whole-recipe coverage 77/86 (89.5%); mean width 27.229 MPa.
- group_max_cqr: row coverage 202/212 (95.3%); whole-recipe coverage 78/86 (90.7%); mean width 33.932 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
