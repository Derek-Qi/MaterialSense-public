# MaterialSense measured experiment

Seed: 51. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **6.288 MPa**; MAE: **4.537 MPa**; R2: **0.8665**; group-balanced RMSE: **5.995 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 17.222 | 13.621 | -0.0018 | 14.713 |
| grouped | ridge | raw | 11.506 | 9.437 | 0.5528 | 9.941 |
| grouped | random_forest | raw | 6.978 | 4.987 | 0.8355 | 6.264 |
| grouped | gradient_boosting | raw | 6.217 | 4.255 | 0.8695 | 5.911 |
| grouped | mean | engineered | 17.222 | 13.621 | -0.0018 | 14.713 |
| grouped | ridge | engineered | 7.530 | 5.934 | 0.8085 | 7.255 |
| grouped | random_forest | engineered | 6.288 | 4.537 | 0.8665 | 5.995 |
| grouped | gradient_boosting | engineered | 5.836 | 4.350 | 0.8850 | 5.459 |
| row_random_diagnostic | mean | raw | 16.365 | 13.296 | -0.0030 | 16.224 |
| row_random_diagnostic | ridge | raw | 9.981 | 8.048 | 0.6268 | 9.529 |
| row_random_diagnostic | random_forest | raw | 5.821 | 4.088 | 0.8731 | 5.746 |
| row_random_diagnostic | gradient_boosting | raw | 6.271 | 4.510 | 0.8527 | 6.211 |
| row_random_diagnostic | mean | engineered | 16.365 | 13.296 | -0.0030 | 16.224 |
| row_random_diagnostic | ridge | engineered | 6.972 | 5.525 | 0.8179 | 6.811 |
| row_random_diagnostic | random_forest | engineered | 5.526 | 3.831 | 0.8856 | 5.368 |
| row_random_diagnostic | gradient_boosting | engineered | 5.557 | 3.920 | 0.8843 | 5.460 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 215/226 (95.1%); whole-recipe coverage 79/86 (91.9%); mean width 26.719 MPa.
- group_max_cqr: row coverage 210/226 (92.9%); whole-recipe coverage 78/86 (90.7%); mean width 28.992 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
