# Repeated MaterialSense benchmark

Fixed seeds; training-only grouped CV selects each point predictor. Random-row results
apply that seed's selected model specification to a different diagnostic test set.
Mean +/- sample SD and min/max describe overlapping resplits, not independent replications
or population confidence intervals. No test-based tuning is performed.

## Selected-model test metrics

| Protocol | Metric | Mean | Sample SD | Min | Max |
|---|---|---:|---:|---:|---:|
| grouped | group_rmse | 5.7165 | 0.6946 | 4.3396 | 6.5904 |
| grouped | mae | 4.1567 | 0.6087 | 3.2281 | 5.3426 |
| grouped | r2 | 0.8782 | 0.0264 | 0.8258 | 0.9127 |
| grouped | rmse | 5.6412 | 0.7884 | 4.2429 | 6.9061 |
| row_random_diagnostic | group_rmse | 5.4324 | 0.3649 | 4.7538 | 6.0072 |
| row_random_diagnostic | mae | 3.7820 | 0.2762 | 3.3745 | 4.1912 |
| row_random_diagnostic | r2 | 0.8952 | 0.0136 | 0.8722 | 0.9134 |
| row_random_diagnostic | rmse | 5.3710 | 0.3205 | 4.9592 | 5.9722 |

## Fixed RandomForest incremental ablation

These nested sets are not the legacy engineered set used in model selection.
Same per-seed partition and frozen forest parameters. Negative paired deltas favor the new set.

| Features | Group RMSE mean | Sample SD | Min | Max |
|---|---:|---:|---:|---:|
| raw | 6.1796 | 0.7071 | 4.9849 | 7.3334 |
| scm_ratio | 5.7479 | 0.8632 | 4.0818 | 7.0548 |
| total_mass | 5.8174 | 0.7111 | 4.6332 | 6.9080 |
| water_binder | 5.6387 | 0.8669 | 4.1038 | 7.0949 |

## Group-maximum intervals
Nominal interval coverage: 90.0%.

| Method | Metric | Mean | Sample SD | Min | Max |
|---|---|---:|---:|---:|---:|
| cqr | mean_width_mpa | 28.6771 | 2.5680 | 24.1239 | 33.9322 |
| cqr | row_coverage | 0.9597 | 0.0203 | 0.9292 | 0.9851 |
| cqr | whole_recipe_coverage | 0.9314 | 0.0242 | 0.8953 | 0.9651 |
| cqr | width_error_spearman | 0.2720 | 0.1046 | 0.1436 | 0.5020 |
| residual | mean_width_mpa | 24.2246 | 2.4729 | 20.8239 | 27.2285 |
| residual | row_coverage | 0.9509 | 0.0259 | 0.8958 | 0.9802 |
| residual | whole_recipe_coverage | 0.9105 | 0.0334 | 0.8488 | 0.9535 |
| residual | width_error_spearman | nan | nan | nan | nan |

Residual interval widths are constant within each seed, so their width/error
correlation is undefined. CQR width need not increase with error or novelty.

## Error-risk alarms

risk_thresholds.csv evaluates absolute prediction error >10 MPa, not a ground-truth
OOD label. Thresholds are quantiles of training-only leave-self-out KNN distances.
Undefined rates remain missing when denominators are zero. Statistical novelty and
physical heuristic screening are separate; neither certifies engineering safety.

## Failure inspection

failures.csv contains the ten largest errors per seed, their actual inputs, intervals
and novelty flags. All test predictions are retained in seed-*/reliability_predictions.csv.
Permutation importance is a post-hoc held-out diagnostic in delta group-RMSE units.
Correlated ingredient/ratio variables make individual importances non-causal.

Exchangeability of historical recipe clusters, including group sizes and measured ages,
is assumed rather than established. Exact recipes do not identify labs/batches or
near-duplicate compositions. Continuous age curves and OOD coverage are not guaranteed.
