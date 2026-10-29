# MaterialSense measured experiment

Seed: 49. Data: 1030 observations, 428 exact recipes.

Training-only grouped CV selected **random_forest / engineered**.
Held-out grouped RMSE: **5.960 MPa**; MAE: **4.550 MPa**; R2: **0.8258**; group-balanced RMSE: **6.212 MPa**.

## Frozen candidate comparison

| Protocol | Model | Features | RMSE (MPa) | MAE (MPa) | R2 | Group RMSE |
|---|---|---|---:|---:|---:|---:|
| grouped | mean | raw | 14.553 | 11.956 | -0.0387 | 12.854 |
| grouped | ridge | raw | 10.134 | 8.148 | 0.4963 | 8.717 |
| grouped | random_forest | raw | 5.817 | 4.325 | 0.8340 | 6.153 |
| grouped | gradient_boosting | raw | 6.007 | 4.429 | 0.8230 | 6.091 |
| grouped | mean | engineered | 14.553 | 11.956 | -0.0387 | 12.854 |
| grouped | ridge | engineered | 6.783 | 5.451 | 0.7743 | 6.684 |
| grouped | random_forest | engineered | 5.960 | 4.550 | 0.8258 | 6.212 |
| grouped | gradient_boosting | engineered | 5.996 | 4.517 | 0.8237 | 6.155 |
| row_random_diagnostic | mean | raw | 17.032 | 13.584 | -0.0105 | 16.430 |
| row_random_diagnostic | ridge | raw | 10.694 | 8.619 | 0.6016 | 10.357 |
| row_random_diagnostic | random_forest | raw | 5.602 | 3.852 | 0.8907 | 5.746 |
| row_random_diagnostic | gradient_boosting | raw | 5.631 | 4.043 | 0.8895 | 5.908 |
| row_random_diagnostic | mean | engineered | 17.032 | 13.584 | -0.0105 | 16.430 |
| row_random_diagnostic | ridge | engineered | 6.959 | 5.480 | 0.8313 | 7.103 |
| row_random_diagnostic | random_forest | engineered | 4.985 | 3.375 | 0.9134 | 5.087 |
| row_random_diagnostic | gradient_boosting | engineered | 4.961 | 3.484 | 0.9143 | 5.191 |

The random and grouped test sets differ. This comparison is descriptive; it is not a causal leakage effect estimate or a demonstrated method improvement.

## Group-maximum calibrated intervals

- group_max_residual: row coverage 172/185 (93.0%); whole-recipe coverage 75/86 (87.2%); mean width 21.815 MPa.
- group_max_cqr: row coverage 174/185 (94.1%); whole-recipe coverage 79/86 (91.9%); mean width 27.335 MPa.

Nominal level and exact denominators are in metadata.json. Guarantees require exchangeable recipe clusters, including their size and age measurement process. The historical compilation does not verify that assumption. CQR is a separate quantile model and does not necessarily contain the selected point estimate.

OOD is a training-distance heuristic, not a coverage repair. Physical input ranges are screening heuristics. This is a public-data case study, not engineering validation.

See docs/methodology.md for the complete protocol and limitations.
