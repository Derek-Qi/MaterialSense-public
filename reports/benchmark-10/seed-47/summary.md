# MaterialSense measured experiment

Seed: 47. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **4.564 MPa**; MAE: **3.419 MPa**; R2: **0.9127**; group-balanced RMSE: **4.858 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 15.503 | 12.773 | -0.0066 | 15.411 |
| grouped | ridge | raw | 10.307 | 8.473 | 0.5550 | 9.729 |
| grouped | random_forest | raw | 6.202 | 4.272 | 0.8389 | 5.667 |
| grouped | gradient_boosting | raw | 6.003 | 4.501 | 0.8491 | 5.889 |
| grouped | mean | engineered | 15.503 | 12.773 | -0.0066 | 15.411 |
| grouped | ridge | engineered | 6.683 | 5.100 | 0.8129 | 7.097 |
| grouped | random_forest | engineered | 4.564 | 3.419 | 0.9127 | 4.858 |
| grouped | gradient_boosting | engineered | 4.655 | 3.590 | 0.9092 | 4.992 |
| row_random_diagnostic | mean | raw | 16.712 | 13.629 | -0.0010 | 16.421 |
| row_random_diagnostic | ridge | raw | 11.120 | 8.877 | 0.5568 | 10.670 |
| row_random_diagnostic | random_forest | raw | 5.044 | 3.544 | 0.9088 | 5.248 |
| row_random_diagnostic | gradient_boosting | raw | 5.294 | 3.810 | 0.8996 | 5.569 |
| row_random_diagnostic | mean | engineered | 16.712 | 13.629 | -0.0010 | 16.421 |
| row_random_diagnostic | ridge | engineered | 7.012 | 5.424 | 0.8238 | 7.094 |
| row_random_diagnostic | random_forest | engineered | 5.243 | 3.549 | 0.9015 | 5.558 |
| row_random_diagnostic | gradient_boosting | engineered | 5.611 | 3.841 | 0.8872 | 5.955 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 194/198 (98.0%); whole-recipe coverage 82/86 (95.3%); mean width 24.918 MPa.
- group_max_cqr: row coverage 195/198 (98.5%); whole-recipe coverage 83/86 (96.5%); mean width 27.806 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
