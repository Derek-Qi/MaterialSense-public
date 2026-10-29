# Protocol and limitations

## Question and unit of generalization

Can a small tabular model predict compressive strength for a previously unseen concrete recipe?
The experimental unit is an exact recipe (cement, slag, fly ash, water, superplasticizer, coarse
aggregate, fine aggregate, in kg/m3). Age in days is an input but not part of recipe identity.
Strength is measured in MPa. Recipe IDs are SHA-256 digests of the seven parsed float64 values in
fixed column order and little-endian representation. Negative zero becomes positive zero. Numeric
formatting such as 200 and 200.0 produces the same key. Distinct representable values remain distinct;
there is no blanket rounding, tolerance clustering, age or target in the key.

This definition only detects exact composition matches. Recipes differing through rounding,
unrecorded material sources, laboratory or curing conditions cannot be identified as related.
The dataset does not expose a laboratory/batch identifier. Near matches can therefore remain across
partitions; this is an explicit limit of the benchmark, not a claim that all dependence is removed.
Exact full-row duplicates are counted and retained because their provenance is unknown. They stay
in one recipe group. They may overweight the row-based metrics, hence group-balanced metrics too.

## Fixed evaluation protocol

Two seeded GroupShuffleSplit calls allocate approximately 60/20/20 of unique groups to training,
calibration and test. Row proportions can differ. A saved assignment file records every row.
GroupKFold runs only inside the training partition; feature scaling is inside each fitted Ridge
pipeline. All feature engineering is deterministic and label-free. The fixed candidate set is mean,
scaled Ridge, RandomForest and GradientBoosting, each with raw and engineered inputs. Selection
minimizes out-of-fold group-balanced RMSE on training recipes. No hyperparameter search is run.
Fitted candidates use training only; calibration is not added back. The test partition is evaluated
after the protocol is fixed, and is never used for selection. Feature ablation is a prespecified
raw-versus-engineered comparison on the same partitions and CV folds.

Engineered features: binder = cement + slag + fly ash; water/binder; water/cement (with an explicit
zero-cement safe denominator); slag/binder; fly ash/binder; superplasticizer/binder; total mass of the
seven ingredients; aggregate/binder; log(1 + age). These are inductive biases, not a physical law.
Materials with different reactivity are not equated by claiming a calibrated effective binder.

The row-random comparison uses the same seed, proportions, model configurations and features. Its
test observations differ from the grouped test observations. Report group overlap and observed
metrics, but do not interpret their difference as a causal estimate of leakage or a proven gain.
Random splitting answers a different question (potential interpolation across ages of known mixes).
It is unsuitable as the primary estimate for unseen recipes; it is not universally invalid for every
possible scientific question.

RMSE, MAE and R2 weight observations equally. Group-balanced RMSE is the square root of the mean
of per-recipe MSE; group-balanced MAE averages per-recipe MAE. Report both because group sizes vary.
A single prespecified seed is an MVP benchmark, not a confidence interval or a robust ranking across
all possible partitions. New tuning after observing test results requires a fresh evaluation plan.

## Group-aware conformal intervals

For residual intervals, compute absolute residuals of the frozen CV-selected point model on
calibration observations. For CQR, fit lower alpha/2 and upper 1-alpha/2 GradientBoosting quantile
regressors using training data and engineered inputs only. Sort the two predicted bounds to handle
crossing. The nonshrinking CQR score is max(lower - y, y - upper, 0). The zero truncation can make
intervals more conservative than canonical signed-score CQR; it prevents interval reversal/shrinkage.

For each method, aggregate scores using the maximum within each calibration recipe. With G
calibration recipes use rank ceil((G + 1)(1 - alpha)) of these G scores. If that rank is G + 1, use
infinity, not a silently capped maximum. Report that no finite interval is available. For residuals
return point +/- q; for CQR return sorted lower - q and upper + q. Do not clip the lower endpoint
at zero or forcibly include the separate point model inside a CQR interval.

Interpretation: conditional on the fitted training model, if calibration recipe clusters and a future
recipe cluster are exchangeable, the same group-maximum scoring rule gives marginal coverage of all
recorded observations in that one new cluster at the nominal level. Different group sizes and age
sampling must be part of this exchangeable cluster-generating process. This does not establish
conditional coverage for every mix or age, simultaneous coverage across many new recipes, coverage
over a continuous age trajectory, or validity after distribution shift. These assumptions are not
verified for the historical UCI compilation. Observed test coverage is reported at both row and
whole-recipe levels, with denominators and widths; subgroup coverage is descriptive only.

Residual intervals have constant width. CQR widths can vary with inputs, but are not an epistemic
uncertainty measure and need not widen for OOD inputs. An OOD warning never modifies interval width
or claims to restore conformal validity. A point prediction from the selected model can fall outside
the separate quantile-model interval; that disagreement should remain visible.

## OOD and physical screening

Standardize the eight raw inputs using training means and scales only. Score a query by its mean
distance to k nearest training observations. Set the warning threshold to the configured empirical
quantile of leave-one-observation-out training distances (request k+1 neighbors and remove one
self-match). This avoids the zero-distance self-neighbor bias. Same-recipe other ages and duplicate
training rows can still be neighbors. This is a heuristic novelty warning, with no calibrated false
alarm rate, no proof of physical infeasibility and no guarantee that all harmful shifts are detected.

Nonnegative ingredients, positive binder, water and age are input validation. Total ingredient mass
outside 2100-2550 kg/m3 and water/binder outside 0.20-0.80 produce configurable screening messages.
These ranges are illustrative normal-weight-concrete heuristics, not building-code limits; mixtures
outside them may be legitimate and passing them does not establish feasibility or safety. The sum
of ingredient masses is not a measured fresh density. Do not use predictions for structural design.

## Sources

- I-Cheng Yeh (1998), [UCI Concrete Compressive Strength](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength),
  DOI [10.24432/C5PK67](https://doi.org/10.24432/C5PK67), CC BY 4.0.
- Romano, Patterson and Candes (2019), [Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222).
- Lee, Barber and Willett, [Distribution-free inference with hierarchical data](https://arxiv.org/abs/2306.06342),
  context for dependence and hierarchical exchangeability. This MVP uses a simpler group-maximum
  rank construction; it does not claim to implement the paper's hierarchical conformal algorithm.
- [scikit-learn GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html).
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing).

