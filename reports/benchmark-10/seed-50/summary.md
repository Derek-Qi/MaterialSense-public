# MaterialSense measured experiment

Seed: 50. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **5.587 MPa**; MAE: **3.950 MPa**; R2: **0.8672**; group-balanced RMSE: **5.363 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 15.650 | 12.645 | -0.0420 | 15.251 |
| grouped | ridge | raw | 9.997 | 7.602 | 0.5748 | 8.930 |
| grouped | random_forest | raw | 5.524 | 4.094 | 0.8702 | 5.539 |
| grouped | gradient_boosting | raw | 5.829 | 4.502 | 0.8554 | 6.191 |
| grouped | mean | engineered | 15.650 | 12.645 | -0.0420 | 15.251 |
| grouped | ridge | engineered | 7.015 | 5.546 | 0.7906 | 7.061 |
| grouped | random_forest | engineered | 5.587 | 3.950 | 0.8672 | 5.363 |
| grouped | gradient_boosting | engineered | 5.430 | 4.119 | 0.8746 | 5.295 |
| row_random_diagnostic | mean | raw | 16.434 | 13.608 | -0.0021 | 16.611 |
| row_random_diagnostic | ridge | raw | 10.013 | 8.030 | 0.6280 | 10.058 |
| row_random_diagnostic | random_forest | raw | 5.886 | 4.519 | 0.8715 | 5.955 |
| row_random_diagnostic | gradient_boosting | raw | 5.470 | 4.098 | 0.8890 | 5.640 |
| row_random_diagnostic | mean | engineered | 16.434 | 13.608 | -0.0021 | 16.611 |
| row_random_diagnostic | ridge | engineered | 6.521 | 4.893 | 0.8422 | 6.741 |
| row_random_diagnostic | random_forest | engineered | 5.596 | 4.092 | 0.8838 | 5.769 |
| row_random_diagnostic | gradient_boosting | engineered | 5.110 | 3.765 | 0.9031 | 5.278 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 180/187 (96.3%); whole-recipe coverage 79/86 (91.9%); mean width 25.530 MPa.
- group_max_cqr: row coverage 180/187 (96.3%); whole-recipe coverage 80/86 (93.0%); mean width 28.411 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
