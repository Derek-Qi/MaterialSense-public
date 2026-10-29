# Prespecified repeated study

Configuration: configs/experiment.yaml plus configs/study.yaml (seeds 42 through 51).
The base seed field is replaced per repetition; each resolved per-seed config is saved.

A. For every seed: group 60/20/20 by exact recipe; use 5-fold GroupKFold inside training to select
mean/Ridge/RandomForest/GradientBoosting and raw/legacy-engineered features. Apply the selected
specification separately to random-row training and test as a diagnostic. No row-random tuning.
metrics.csv retains all candidate scores and selected flags. split_audit.csv includes every
partition pair's sizes, shared recipe IDs, distinct shared complete nine-variable rows, and the
number of B-partition copies found in A. The latter column has a legacy long name
test_rows_duplicated_in_train; interpret it using the pair field (train_test is the headline pair).

B. Independently fix the RandomForest parameters to the base config. On the same grouped split
compare nested raw eight inputs; +water/binder; +SCM ratio; +total mass. Binder=cement+slag+fly ash
(kg/m3), water/binder=water/binder (dimensionless), SCM=(slag+fly ash)/binder (dimensionless),
total mass=sum of seven materials (kg/m3). Age remains days. Legacy engineered features include
other descriptors and are not the same as this last nested set. Save paired deltas against raw.
Five permutation repeats on held-out nested-total-mass inputs measure delta group-balanced RMSE.
They explain a frozen model after evaluation and never select a model. Correlated inputs limit
individual attribution; importances can be negative and are not causal effects.

C. Fit residual and sorted, nonshrinking CQR bounds on training only; one maximum nonconformity
score per calibration recipe. Correct at finite-sample rank ceil((G+1)*.9). Evaluate row coverage,
complete-recipe coverage and width on untouched test groups. Width/error Spearman correlation uses
selected-point absolute error; CQR is a separate model so mismatch is possible. Constant residual
width has undefined correlation. This evaluates recorded age sets, assumes exchangeable clusters,
and does not guarantee OOD, conditional or simultaneous continuous-curve coverage.

D. Use mean 5-neighbor distance in training-standardized raw input space. Training leave-self-out
distance quantiles .80/.90/.95/.99 define fixed risk thresholds. The default dashboard threshold
stays .95; none is chosen by test performance. The event is prespecified absolute prediction error
>10 MPa, not an observed ground-truth OOD label. Report TP/FP/FN/TN, precision/recall, false positive/
negative rates and flagged/unflagged MAE. Empty denominators remain missing, not zero. Threshold
comparisons are exploratory diagnostics, not a guarantee or a threshold optimization experiment.

All mean/SD/min/max use ten overlapping resplits; sample SD uses ddof=1. They describe sensitivity
to partitions and stochastic fits. They are not ten independent material experiments and are not
confidence intervals for a population. Different grouped/random test rows prevent interpreting
their difference as an isolated causal leakage effect. Historical lab dependence remains unknown.

Study outputs refuse a nonempty destination. No implicit resume or overwrite is supported. If
interrupted, retain that directory for inspection and start a new output path. manifest.json is
written only after every seed and report completes; it records source/data/config hashes, environment
and checksums of every result/model. A missing complete manifest means an incomplete study.
